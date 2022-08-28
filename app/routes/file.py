import os

from fastapi import APIRouter, status, HTTPException, File, UploadFile, BackgroundTasks
from fastapi.responses import FileResponse

from .. import schema, utils
from ..config import settings
from ..custom import CustomRequest, CustomResponse, CustomRoute

router = APIRouter()
router.route_class = CustomRoute

"""

##### All File Routes

: Upload new file
: Get file

"""

@router.post("/upload")
def upload(request: CustomRequest, response: CustomResponse, background_tasks: BackgroundTasks, file: UploadFile = File()):
    # Get content type header
    # use Accept headers to return xml or json data of file
    media_type = request.headers.get('Accept')

    # Check file exist
    if not file:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='image no found')

    # Get new uuid filename and extension 
    filename, extension = utils.generate_filename(file.filename)
     
    # Check extension of file 
    if extension not in settings.FILE_EXTENSIONS:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="extension no acceptable")

    # File Content
    contents = file.file.read()

    # Path and Url
    path = os.path.abspath(os.path.join("upload", "images", f"{filename}"))
    url = f"{request.base_url}api/file/getfile/{filename}"
    
    # Write file
    try:
        background_tasks.add_task(utils.write_file, path, contents)
    except Exception:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='file upload failed')
    finally:
        file.file.close()

    # Set response file url and status code
    response = CustomResponse(content={ 'status': 'success', 'url': url }, media_type=media_type, custom_root='file')
    response.status_code = status.HTTP_201_CREATED

    # Send response
    return response

@router.get("/getfile/{filename}", status_code=status.HTTP_200_OK)
def getfile(filename: str):
    # Create path of file
    image_path = os.path.abspath(os.path.join("upload", "images", f"{filename}"))
    
    # Check file exist
    if not os.path.exists(image_path):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='file not found')

    # Send file in response 
    return FileResponse(image_path)
