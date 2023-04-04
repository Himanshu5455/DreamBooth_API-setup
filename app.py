from flask import Flask, request, render_template, redirect, jsonify
import os
import requests
import json
from multiprocessing.dummy import Pool
from dreambooth import ApiDataBuilder
from dbConnect import dbConnect
import base64

app = Flask(__name__)

pool = Pool(10)
futures = []


app = Flask("_name__")

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template("home.html")
# TODO: REFECTOR THE HOME.HTML TO GET NAVBAR


#Home page i.e Generator

@app.route('/generator', methods=['GET', 'POST'])
def generator():
    global futures
    futures = []

    data = json.loads((request.data).decode('utf-8'))
    aspectRatio = data.pop("aspectRatio")
    dreambooth = ApiDataBuilder()
    payload = dreambooth.setPayload(data, aspectRatio)
    print("payload",payload)
    url = "https://stablediffusionapi.com/api/v3/text2img"
    
    futures.append(pool.apply_async(requests.post, [url], {'data': payload}))
    return "Request sent to api server"



#displayes images on screen
@app.route('/show_images', methods=['GET', 'POST'])
def show_images():
    for future in futures:
        r = future.get()
        # TODO: Handle jsondecodeError
        r_dict = r.json()

    if len(futures) != 0:
        if r.status_code == 200:
            if r_dict["status"] == "success":              
                if len(r_dict["output"]) != 0:
                    image_urls = r_dict['output']
                    return render_template("show_images.html", image_names=image_urls)
                else:
                    return f"Something went wrong.json data is {r_dict}"
            elif r_dict["status"] == "processing":
                id = str(r_dict["id"])
                # TODO: REFECTOR THE CODE FOR SINGLE STATIC DIR
                return render_template('image_processing.html', id=id)
            else:
                return "<center>Status is 200 but it is neither success nor processing.<br>Request has not been called0.<br>Please re-try.</center>"
        else:
            return "404 ERROR"
    else:
        return "<center>Request is not Sent(length of futures is 0).<br>Please re-try</center>"
    # return str(r.status_code) + str(r_dict["messege"])



#Upscale image from show_images 


@app.route('/upscale', methods=['GET', 'POST'])
def deepAIupscale():
    try :
        if request.method == "GET":
            args = request.args
            path = args.get("path")
            print(path)

            r = requests.get(
                f'{path}')
            path_cwd = os.path.dirname(os.path.realpath(__file__))
            upscale_path = os.path.join(path_cwd, "static/upscaleThis")
            with open(f'{upscale_path}/image.jpg', 'wb') as f:
                f.write(r.content)
            return render_template('upscaling.html', context=path)
        
        elif request.method == "POST":

            new_data = request.values.get('new_freq')          
            print(type(new_data))
            #open image 
            with open('static/upscaleThis/image.jpg','rb') as img_file :
                file = base64.b64encode(img_file.read()).decode('utf-8')   

            response = requests.post("https://doevent-face-real-esrgan.hf.space/run/predict", json={
            "data": [
                "data:image/jpg;base64,"+ file,
                str(new_data),
            ]
            }).json()

            #encoded text
            encoded_data = response["data"][0][22:]

            #decode base64 string data
            decoded_data=base64.b64decode((encoded_data))

            print("image is now ready")
            #write the decoded data back to original format in  file
            img_file = open('static/upscale/image1.jpeg', 'wb')
            img_file.write(decoded_data)
            img_file.close()

            return "Upscaling your image"

        else :
            return "neither POST nor GET request"
        
    except :
        return "<center><p>Click on Upscale button to Upscale</p></center>"

#Download Image From 
@app.route('/download', methods=["GET", "POST"])
def downloadurl():

    try:
        if request.method == "GET":
            args = request.args
            image_url = args.get("path")
            r = requests.get(
                f'{image_url}')
            path_cwd = os.path.dirname(os.path.realpath(__file__))
            download_path = os.path.join(path_cwd, "static/download")
            with open(f'{download_path}/image.jpg', 'wb') as f:
                f.write(r.content)
        return render_template('direct_download.html')
    except :
        return "<center><p>didn't Find the Image<hr>Please re-try</p></center>"

@app.route('/upscaledImage',methods=['GET',"POST"])
def downloadUpscaledImage():    
        return render_template('downloadImage.html')


#fetch Images from Id
@app.route('/fetch_images', methods=['GET', 'POST'])
def IMAGES():
    if request.method == 'POST':
        fid = request.form["fid"]
        print(fid)
        try:
            img_urls = serve_images(fid)
            if len(img_urls) == 0:
                return "<center><h1> Id doesnt Exixts </h1></center>"
            return render_template("show_images.html", image_names=img_urls)
        except FileNotFoundError as e:
            return f"processing you images{e}"
    return render_template("get_fine_tune_id.html")



@app.route('/parseId',methods=["GET","POST"])
def parseId():
    data= request.form["my_input"]
    return render_template("filledInput.html",data=data)




def  serve_images(fid):
    conn = dbConnect()
    cursor = conn.cursor()
    cursor.execute(f"SELECT image FROM imagestore where id = {fid}")
    list_images = cursor.fetchall()
    conn.close()
    if len(list_images) != 0:
        list_images = [url.strip() for url in list_images[0][0].replace('{', '').replace('}', '').split(',')]
        return list_images
    else:
        return 0


#Training model status

@app.route('/getTrainingStatus', methods=['GET', 'POST'])
def getTrainingStatus():
    if request.method == 'POST':
        trainingId = request.form["trainingid"]
        key = request.form["key"]
        url = f"https://stablediffusionapi.com/api/v3/fine_tune_status/{trainingId}"
        payload = json.dumps({
            "key": key
        })
        headers = {
            'Content-Type': 'application/json'
        }
        post_response = requests.request("POST", url, headers=headers, data=payload).json()
        try:
            return render_template('trainingidResponse.html', post_response=post_response)
        except Exception as e:
            return render_template('trainingid.html', error='Error making API request: {}'.format(e))
    return render_template('trainingid.html')


#history

@app.route('/history', methods=["POST", "GET"])
def history():
 
    # Set number of records per page
    RECORDS_PER_PAGE = 2

    my_dict = {}

    # Get current page number from URL parameters
    page = request.args.get('page', 1, type=int)
    # Calculate offset to fetch the right page
    offset = (page - 1) * RECORDS_PER_PAGE

    conn = dbConnect()
    curr = conn.cursor()

    # Query to fetch data with pagination
    query = "Select * From imagestore ORDER BY id DESC LIMIT %s OFFSET %s;"

    curr.execute(query, (RECORDS_PER_PAGE, offset))
    data = curr.fetchall()

     # Count total number of rows in table
    curr.execute("SELECT COUNT(*) FROM imagestore")
    total_rows = curr.fetchone()[0]
    curr.close()

    for i in range(len(data)):
        id = data[i][0]
        list_images = [url.strip() for url in data[i][1].replace('{', '').replace('}', '').split(',')]
        my_dict[id] = list_images

    total_pages = (total_rows + RECORDS_PER_PAGE - 1) // RECORDS_PER_PAGE
    # Render HTML template with data and pagination variables
    return render_template("history.html", record=my_dict, page=page, total_pages=total_pages)
  

#Train Model
@app.route('/TrainModel', methods=['GET', 'POST'])
def fineTuning():
    
    if request.method == 'POST':
        payload = dict(request.form)
        payload.pop("image_7")
        direct_image_urls = request.form.getlist('image_7')
        detault_payload = {
            "images": direct_image_urls,
            "seed": "0",
            "max_train_steps": "2000",
            "webhook": "https://0444-182-70-252-19.in.ngrok.io"
        }
        payload.update(detault_payload)
        print("payload is",payload)
        images = []
        print("direct_image_urls are ",direct_image_urls)
        for image in direct_image_urls:
            # check if image exists
            if image:
                if allowed_file(image):
                    return render_template('images.html', error='Invalid file type')
                else:
                    try:
                        images.append(image)
                    except Exception as e:
                        return render_template('images.html', error='Error saving file: {}'.format(e))

        try:
            url = "https://stablediffusionapi.com/api/v3/fine_tune"
            headers = {
                'Content-Type': 'application/json'
            }
            response = requests.request("POST", url, headers=headers, data=payload).json()
            if response["status"] == "success":
                print("post request is sent")
                return render_template('trainingResponse.html', post_response=response)
            else:
                print("post request is denied")
                return f"{response}"
        except Exception as e:
            return render_template('images.html', error='Error making API request: {}'.format(e))
    print("request was not post")
    return render_template('images.html')


#generate Images from our Trianed model
@app.route('/getFineTunedImages', methods=['GET', 'POST'])
def getFineTunedImage():
    if request.method == 'POST':
        url = 'https://stablediffusionapi.com/api/v3/dreambooth'
        data = (request.data).decode('utf-8')
        data = json.loads(data)
        aspectRatio = data.pop("aspectRatio")
        dreambooth = ApiDataBuilder()
        payload = dreambooth.setPayload(data, aspectRatio)
        print(payload)
        global futures
        futures = []
        futures.append(pool.apply_async(requests.post, [url],
                                        {'data': payload}))
        return "Request to get fine tuned images is sent to api server"
    return render_template('index.html')







#webhook
@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        return json.dumps({
            "status": "online",
            "message": "Server is running properly!"
        })

    if request.method == 'POST':
        data = request.json
        if data["status"] == "success":
            if "data" in data.keys():
                image_urls: list = data["data"]["output"]
                fetchid = data["id"]
                with open("last_id.txt", "w") as f:
                    f.write(str(fetchid))
            else:
                image_urls = data["output"]
                fetchid = data["id"]
                with open("last_id.txt", "w") as f:
                    f.write(str(fetchid))
            conn = dbConnect()
            curr = conn.cursor()
            curr.execute("INSERT INTO imagestore (id, image) VALUES (%s,%s)", (fetchid, image_urls))
            conn.commit()
            conn.close()
            return "Stored image's url in database"
        return "ok"










# validation of images
def allowed_file(urls):
    ALLOWED_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.gif', '.bmp']
    for url in urls:
        for format in ALLOWED_EXTENSIONS:
            if url.endswith(format):
                return True
    return False





if __name__ == '__main__':
    app.run()

