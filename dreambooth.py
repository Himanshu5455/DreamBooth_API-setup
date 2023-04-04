class ApiDataBuilder:
    aspectRatios = {
        "Cinema": [1024, 576],
        "Landscape": [1080, 720],
        "Square": [512, 512],
        "Tablet": [720, 1080],
        "Phone": [576, 1024],
        "default": [512, 512]
    }

    def setHeightWidth(self,aspectRatio = "default"):
        return self.aspectRatios[aspectRatio] if aspectRatio in self.aspectRatios.keys() else [512,512]

    def setPayload(self,data,aspectRatio = "default"):
        aspectRatio = self.setHeightWidth(aspectRatio)
        self.__dict__.update(PAYLOAD = {
            "key": "3q5yKsnSQQZovB8dkV0SoSsGkKGlgkMguwQC82IyxKJjUyO1JTvOz0OrDS94", #.env me set karni hai
            "num_inference_steps": "20",
            "safety_checker": "no",
            "seed": None,
            "guidance_scale": 7.5,
            "webhook": "http://65.2.35.162/webhook", #.env me set karni hai
            "track_id": None,
            "width": aspectRatio[0],
            "height": aspectRatio[1]
        })
        self.__dict__["PAYLOAD"].update(data)
        return self.__dict__["PAYLOAD"]
