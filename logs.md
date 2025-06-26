# Deployment
- Railway and most other deployment services do not support opening devices like webcam, so the live attendance capturing feature only works locally, I am looking to make it such that it works via file upload client side or using an external ESP module(i.e the ESP CAM module) for image capturing and face recognition.
- But for now the rest of the app's functioning is deployed on https://smart-attendance-system-production-0088.up.railway.app/
- You could also try all of the app's fuctionality locally on your PC, just follow these steps:
  
### 1. Clone
```bash
git clone https://github.com/Enochteo/smart-attendance-system.git
cd smart-attendance-system
```
### 2. Set up a virtual env
```bash
python -m venv venv
source venv/bin/activate
```
### 3. Install dependencies
```bash
pip install -r requirements.txt
```
### 4. Create your stored images directory
<!--- Name it "student-faces"
To use your own faces:
Place JPG images in the `students_faces/` folder.
The filename will be used as the name label.--->
You can now upload your students pictures via the upload route

### 5. Run
```bash
python app.py
```
Then visit http://127.0.0.1:5000
