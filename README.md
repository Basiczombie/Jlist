# JList
---

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
- File segregation based on user permissions.
- File validation based on MIME type and file extension.
- Upload date displayed.
- User Upload name displayed.
- Anonymous upload.

### Design Process:

**Models**

JList was approached from the models up. By reviewing the required features of the project a set of data points were identified to best represent the need for the application. Understanding the data needs for the application at the start is always the best guide to inform later decisions.

***Jfile***
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

Adding a str method to return the filename from the filefield upon any querying is highly recommended. In addition setting verbose_name_plural in the models meta class and a preset ordering is also helpful.

After setting the fields insure to tell Django to ```makemigrations``` and ```migrate``` the schema to the database.

**Views**

In Django the View is the controller in the MVC model. With the data identified and represented in the models it is now possible to create controllers that will be linked by urls and templates to render data.

By the features required, JList needs to be able render a full list of all uploaded JSON files, sort that list by user group, allow a user to download a uploaded file, and allow for users to upload files.

Some these tasks can be accomplished by the same View. As such, there will only need to be three views for this application.

***JsonListView***
- Django generic view ```ListView``` linked to ```model_name``` in ```models```.
- Custom Queryset:
    - Queryset will be filtered by ```user.group```.
    - If the user is not authenticated and is not in the group ```JLIST_ADMIN``` then return a queryset that excludes all model objects whose privacy is marked as ```'PRIVATE'```. Else, return all model objects.
    - With Django the data could be filtered at the View or Template level. By creating the data set at the controller level there is greater control over data manipulation and transformation. It also keeps the business logic in the backend were it belongs simplifying template requirements.

***JsonFileUploadView***
- Django generic view ```CreateView``` linked to model_name in models.
- For this view it will be necessary to use a ```form_class``` linking to a custom form. The form will be where the ```JSON``` file will be cleaned and validated.
- Ensure to set the ```success_url```. This url should redirect the user back to the ```JsonListView```.
- Custom form validation:
    - Override ```form_vaild``` and set ```commit=False```
    - Check if submitting user is authenticated. If yes then set username to ```model.user``` field. If no then set ```'anonymous'``` to ```model.user``` field.
    - Set current datetime to ```model.upload_date```.
        - Django datetime fields have an ```auto_now``` option that is supposed to set the datetime upon model creation. It is at user's discretion to set it or set datetime directly.
    - Save the model and return. This will automatically call the ```success_url```.

***JsonFileView***
- Django generic view ```View```.
- This view gives access to the ```get``` method without requiring anything else. This enables a call from another view without requiring any template rendering.
- Allows for Ajax like functionality without having to use Ajax.
- This view will enable download functionality through a ```HttpResponse```.
- The view will need to be able to do the following:
    - Query the requested file by the primary key and the first result.
    - Create a ```filename``` from the queried file.
        - The current ```filename``` will be the absolute path to the file in media.
        - The ```filename``` will require some manipulation to remove the path.
    - The ```file_path``` from media will need to be defined.
    - The ```file_path``` will need to be opened by ```FileWrapper``` with ```open(file_path,'rb')``` as the parameter.
    - The file ```mimetype``` will need to be defined by the python ```mimetypes.guess_types``` option.
    - A ```HttpResponse``` will need to be created taking the opened ```file_path``` and the ```content_type``` set to the ```mimetype```.
    - Once the ```response``` is created it will need some modification.
    - The ```response['X-Sendfile']``` will need to be set to the ```file_path```.
    - The ```response['Content-Length']``` will need to be set.
        - hint: ```os.stat(file_path).st_size```
    - The ```response['Content-Disposition']``` will need to be set to the attached file.
        - hint: ```'attachment; filename={}/'.format(smart_str(file_name))```
    - Then return the ```response```.

**Forms**

If not already done so create a Form.py in the application folder. This is where the form for JList will be created and then imported into the Views.

The goal of this form is to use Django's formfactory to render the form, clean the data of any possible injection, and validate the file to uploaded. A future consideration would be to run an antivirus, like [ClamAV](https://www.clamav.net/), that would scan the file durning the clean step to help weed out malicious files.

***JfileForm***
- This form should validate the file to JSON and that the file sizes does not exceed 1MB in size.
- From .models import model_name.
- Set the class meta:
    - Model will be model_name.
    - For fields the form will only need the ```filefield``` and ```privacy```
- Create a method for file validation.
    - This method should check both the mimetype and the file extension.
    - Some mimetype libraries only check file extension. [Python-Magic](https://github.com/ahupp/python-magic) is recommended for python mimetype validation.
    - The mimetype should present as ```'text/plain'``` with this method.
    - Using python sting options the extinction should be collected from the filename.
    - If the mimetype and the extension are correct then return true, else false.
- Create a clean method.
    - In the clean get a clean copy of the file.
    - Test if the file is not larger than 1MB.
        - ```file > (2**20)```
    - Test that the file is not a JSON through the validation method.
    - If either of those is True return a Validation Error.
    - else return the cleaned_data.

**Urls**

Create a Urls.py that will be included in the config/urls.py. This url file will import the Views and connect them to be served. Setting the ```app_name``` is a handy way to keep url namespaces short and easy to handle.

- For the download link it will be necessary for the url to take the primary key of the model that contains the file requested for download.
- To do this with Django 2.0+, all that is required is ```'downloads/<int: pk>'``` as the url path.

**Admin**

Insure to set up the Admin to give the logged in user the ability to administrate the model objects.

**Templates**

Now that all the backend data has been determined all that remains are the templates. FOr this project there are only three templates, one base, and two more that will render the home display and form.

***Base HTML***
- The base html will allow Django's templating engine to load all css and scripts across each template that will extended it. It will also enable the creation of blocks that will display any content created between them from the extended templates. This helps cut down the clutter in the other templates.
- Setting up a CSS framework like Bootstrap, Materialize, Foundation, or other can be done here.

***JSON List HTML***
- This template will need to render the data from ```JsonListView```.
- The following items are required to be displayed.
    - File
    - Size
    - User
    - Upload Date
- A link will need to be created on the File to download url with the file's primary key passed with it.
- A link to the form creation url will also need to be displayed on the page.

***Jfile Form HTML***
- The Django ```{{ form }}``` will need to be wrapped in a form tag.
- Ensure that the ```form``` tag has the following:
    - ``` method="post"```
    - ```enctype="multipart/form-data"```
    - The file will not be accepted if the ```enctype``` is not set.
- Ensure that within the ```form``` tag the ```{% csrf_token %}``` is set. Without it the file will not be accepted.
- Django formfactory will generate all the fields in the HTML that were defined in the Forms.py.
