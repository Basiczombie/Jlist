# JList

#### Directory Map
```
| + jlist (Root Directory)
| - + jlist (Application Directory)
| - - + migrations (ORM DB Relationship Files)
| - - + templates (Application HTML Templates)
| - + config (DJANGO Setting Files)
```

### Overview

JList is a web application designed to serve JSON uploaded files.

**Features:**
- File segeration based on user permissions.
- File validation based on MIME type and file extention.
- Upload date displayed.
- User Upload name displayed.
- Anonymous upload.

### Design Process:

**Models**
JList was approached from the models up. By reviewing the required features of the project a set of data points were identified to best represent the need for the application. Understanding the data needs for the application at the start is always the best guide to inform later decisions.

*JList required four data points:*
- **jfile**
    - A file field required to store the file path for the JSON file to be uploaded
    - Insure that the upload_to path is set up in settings to place the files into the media folder to be served by the webserver.
- **upload_date**  
    - A datetime field required to store the timestamp of when the file was uploaded set to record at the objects creation.
- **user**
    - A character field that will store the username of the logged in user that uploads a file or anonymous if no user is authenticated.
- **privacy**
    - A character field with a choices option linked to a list of possible dropdown options. By using this method over a boolean field the application gains scalability to include more groups at a later time.
    - This field requires a list of options. This list can be a tuple set up in the model itself or as a Foreign Key relation to another model depending on scale and desire.

*Notes*
Adding a str method to return the filename from the filefield upon any querying is highly recommended. In addition Setting verbose_name_plural in the models meta class and a preset ordering is also helpful.

**Views**
In Django the View is the controller in the MVC model. With the data identified and represented in the models it is now possible to create controllers that will be linked by urls and templates to render data.

By the features required JList needs to be able render a full list of all uploaded JSON files, sort that list by user group, allow a user to download a uploaded file, and allow for users to upload files.

Some these tasks can be accomplished by the same View. As such, there will only need to be three views for this application.

***JsonListView***
- Django generic view ```ListView``` linked to ```model_name``` in ```models```.
- Custom Queryset:
    - Queryset will be filtered by ```user.group```.
    - If the user is not authenticated and is not in the group ```JLIST_ADMIN``` then return a queryset that excludes all model objects whose privacy is marked as ```'PRIVATE'```. Else, return all model objects.

***JsonFileUploadView***
- Django generic view ```CreateView``` linked to model_name in models.
- For this view it will be necessary to use a ```form_class``` linking to a custom form. The form will be where the ```JSON``` file will be cleaned and validated.
- Ensure to set the ```success_url```. This url should redirect the user back to the ```JsonListView```.
- Custom form validation:
    - Override ```form_vaild``` and set ```commit=False```
    - Check if submitting user is authenticated. If yes then set username to ```model.user``` field. If no then set ```'anonymous'``` to ```model.user``` field.
    - set current datetime to ```model.upload_date```.
        - Django datetime fields have an ```auto_now``` option that is supposed to set the datetime upon model creation. It is at user's discretion to set it or set datetime directly.
    - Save the model and return. This will automatically call the ```success_url```.

***JsonFileView***
- Django generic view ```View```.
- This view gives access to the ```get``` method without requiring anything else. This enables a call from another view without requiring any template rendering.
- Allows for Ajax like functionality without having to use Ajax.
- This view will enable download functionality through a ```HttpResponse```.
- The view will need to be able to do the following.:
    - query the requested file by the primary key and the first result.
    - create a ```filename``` from the queried file.
        - The current ```filename``` will be the absolute path to the file in media.
        - The ```filename``` will require some manipulation to remove the path.
    - The ```file_path``` from media and the ```filename``` will need to be defined.
    - The ```file_path``` will need to be opened by ```FileWrapper``` with the tags 'rb'.
    - The file ```mimetype``` will need to be defined.
    - A ```HttpResponse``` will need to be created taking the opened ```file_path``` and the ```content_type``` set to the ```mimetype```.
    - Once the ```response``` is created it will need some modification.
    - The ```response['X-Sendfile']``` will need to be set to the ```file_path```.
    - The ```response['Content-Length']``` will need to be set.
        - hint: ```os.stat(file_path).st_size```
    - The ```response['Content-Disposition']``` will need to be set to the attached file.
        - hint: ```'attachment; filename={}/'.format(smart_str(file_name))```
    - Then return the ```response```.

**Forms**





 

