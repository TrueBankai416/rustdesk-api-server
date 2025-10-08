import io
from pathlib import Path
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.files.base import ContentFile
import os
import re
import requests
import base64
import json
import uuid
import pathlib
from django.conf import settings as _settings
from django.db.models import Q
from .forms import GenerateForm
from .models import GithubRun
from PIL import Image
from urllib.parse import quote

@login_required(login_url='/api/user_action?action=login')
def generator_view(request):
    if request.method == 'POST':
        form = GenerateForm(request.POST, request.FILES)
        if form.is_valid():
            platform = form.cleaned_data['platform']
            version = form.cleaned_data['version']
            delayFix = form.cleaned_data['delayFix']
            cycleMonitor = form.cleaned_data['cycleMonitor']
            xOffline = form.cleaned_data['xOffline']
            hidecm = form.cleaned_data['hidecm']
            removeNewVersionNotif = form.cleaned_data['removeNewVersionNotif']
            server = form.cleaned_data['serverIP']
            key = form.cleaned_data['key']
            apiServer = form.cleaned_data['apiServer']
            urlLink = form.cleaned_data['urlLink']
            downloadLink = form.cleaned_data['downloadLink']
            if not server:
                server = 'rs-ny.rustdesk.com' #default rustdesk server
            if not key:
                key = 'OeVuKk5nlHiXp+APNn0Y3pC1Iwpwn44JGqrQCsWqmBw=' #default rustdesk key
            if not apiServer:
                apiServer = server+":21114"
            if not urlLink:
                urlLink = "https://rustdesk.com"
            if not downloadLink:
                downloadLink = "https://rustdesk.com/download"
            direction = form.cleaned_data['direction']
            installation = form.cleaned_data['installation']
            settings = form.cleaned_data['settings']
            appname = form.cleaned_data['appname']
            filename = form.cleaned_data['exename']
            compname = form.cleaned_data['compname']
            if not compname:
                compname = "Purslane Ltd"
            compname = compname.replace("&","\\&")
            permPass = form.cleaned_data['permanentPassword']
            theme = form.cleaned_data['theme']
            themeDorO = form.cleaned_data['themeDorO']
            runasadmin = form.cleaned_data['runasadmin']
            passApproveMode = form.cleaned_data['passApproveMode']
            denyLan = form.cleaned_data['denyLan']
            enableDirectIP = form.cleaned_data['enableDirectIP']
            #ipWhitelist = form.cleaned_data['ipWhitelist']
            autoClose = form.cleaned_data['autoClose']
            permissionsDorO = form.cleaned_data['permissionsDorO']
            permissionsType = form.cleaned_data['permissionsType']
            enableKeyboard = form.cleaned_data['enableKeyboard']
            enableClipboard = form.cleaned_data['enableClipboard']
            enableFileTransfer = form.cleaned_data['enableFileTransfer']
            enableAudio = form.cleaned_data['enableAudio']
            enableTCP = form.cleaned_data['enableTCP']
            enableRemoteRestart = form.cleaned_data['enableRemoteRestart']
            enableRecording = form.cleaned_data['enableRecording']
            enableBlockingInput = form.cleaned_data['enableBlockingInput']
            enableRemoteModi = form.cleaned_data['enableRemoteModi']
            removeWallpaper = form.cleaned_data['removeWallpaper']
            defaultManual = form.cleaned_data['defaultManual']
            overrideManual = form.cleaned_data['overrideManual']
            enablePrinter = form.cleaned_data['enablePrinter']
            enableCamera = form.cleaned_data['enableCamera']
            enableTerminal = form.cleaned_data['enableTerminal']

            if all(char.isascii() for char in filename):
                filename = re.sub(r'[^\w\s-]', '_', filename).strip()
                filename = filename.replace(" ","_")
            else:
                filename = "rustdesk"
            if not all(char.isascii() for char in appname):
                appname = "rustdesk"
            myuuid = str(uuid.uuid4())
            protocol = _settings.PROTOCOL
            host = request.get_host()
            full_url = f"{protocol}://{host}"
            try:
                iconfile = form.cleaned_data.get('iconfile')
                if not iconfile:
                    iconfile = form.cleaned_data.get('iconbase64')
                iconlink = save_png(iconfile,myuuid,full_url,"icon.png")
            except:
                print("failed to get icon, using default")
                iconlink = "false"
            try:
                logofile = form.cleaned_data.get('logofile')
                if not logofile:
                    logofile = form.cleaned_data.get('logobase64')
                logolink = save_png(logofile,myuuid,full_url,"logo.png")
            except:
                print("failed to get logo")
                logolink = "false"

            ###create the custom.txt json here and send in as inputs below
            decodedCustom = {}
            if direction != "both":
                decodedCustom['conn-type'] = direction
            if installation == "installationN":
                decodedCustom['disable-installation'] = 'Y'
            if settings == "settingsN":
                decodedCustom['disable-settings'] = 'Y'
            if appname.upper != "rustdesk".upper and appname != "":
                decodedCustom['app-name'] = appname
            decodedCustom['override-settings'] = {}
            decodedCustom['default-settings'] = {}
            if permPass != "":
                decodedCustom['password'] = permPass
            if theme != "system":
                if themeDorO == "default":
                    if platform == "windows-x86":
                        decodedCustom['default-settings']['allow-darktheme'] = 'Y' if theme == "dark" else 'N'
                    else:
                        decodedCustom['default-settings']['theme'] = theme
                elif themeDorO == "override":
                    if platform == "windows-x86":
                        decodedCustom['override-settings']['allow-darktheme'] = 'Y' if theme == "dark" else 'N'
                    else:
                        decodedCustom['override-settings']['theme'] = theme
            decodedCustom['enable-lan-discovery'] = 'N' if denyLan else 'Y'
            decodedCustom['allow-auto-disconnect'] = 'Y' if autoClose else 'N'
            if permissionsDorO == "default":
                decodedCustom['default-settings']['access-mode'] = permissionsType
                decodedCustom['default-settings']['enable-keyboard'] = 'Y' if enableKeyboard else 'N'
                decodedCustom['default-settings']['enable-clipboard'] = 'Y' if enableClipboard else 'N'
                decodedCustom['default-settings']['enable-file-transfer'] = 'Y' if enableFileTransfer else 'N'
                decodedCustom['default-settings']['enable-audio'] = 'Y' if enableAudio else 'N'
                decodedCustom['default-settings']['enable-tunnel'] = 'Y' if enableTCP else 'N'
                decodedCustom['default-settings']['enable-remote-restart'] = 'Y' if enableRemoteRestart else 'N'
                decodedCustom['default-settings']['enable-record-session'] = 'Y' if enableRecording else 'N'
                decodedCustom['default-settings']['enable-block-input'] = 'Y' if enableBlockingInput else 'N'
                decodedCustom['default-settings']['allow-remote-config-modification'] = 'Y' if enableRemoteModi else 'N'
                decodedCustom['default-settings']['direct-server'] = 'Y' if enableDirectIP else 'N'
                decodedCustom['default-settings']['verification-method'] = 'use-permanent-password' if hidecm else 'use-both-passwords'
                decodedCustom['default-settings']['approve-mode'] = passApproveMode
                decodedCustom['default-settings']['allow-hide-cm'] = 'Y' if hidecm else 'N'
                decodedCustom['default-settings']['allow-remove-wallpaper'] = 'Y' if removeWallpaper else 'N'
                decodedCustom['default-settings']['enable-remote-printer'] = 'Y' if enablePrinter else 'N'
                decodedCustom['default-settings']['enable-camera'] = 'Y' if enableCamera else 'N'
                decodedCustom['default-settings']['enable-terminal'] = 'Y' if enableTerminal else 'N'
            else:
                decodedCustom['override-settings']['access-mode'] = permissionsType
                decodedCustom['override-settings']['enable-keyboard'] = 'Y' if enableKeyboard else 'N'
                decodedCustom['override-settings']['enable-clipboard'] = 'Y' if enableClipboard else 'N'
                decodedCustom['override-settings']['enable-file-transfer'] = 'Y' if enableFileTransfer else 'N'
                decodedCustom['override-settings']['enable-audio'] = 'Y' if enableAudio else 'N'
                decodedCustom['override-settings']['enable-tunnel'] = 'Y' if enableTCP else 'N'
                decodedCustom['override-settings']['enable-remote-restart'] = 'Y' if enableRemoteRestart else 'N'
                decodedCustom['override-settings']['enable-record-session'] = 'Y' if enableRecording else 'N'
                decodedCustom['override-settings']['enable-block-input'] = 'Y' if enableBlockingInput else 'N'
                decodedCustom['override-settings']['allow-remote-config-modification'] = 'Y' if enableRemoteModi else 'N'
                decodedCustom['override-settings']['direct-server'] = 'Y' if enableDirectIP else 'N'
                decodedCustom['override-settings']['verification-method'] = 'use-permanent-password' if hidecm else 'use-both-passwords'
                decodedCustom['override-settings']['approve-mode'] = passApproveMode
                decodedCustom['override-settings']['allow-hide-cm'] = 'Y' if hidecm else 'N'
                decodedCustom['override-settings']['allow-remove-wallpaper'] = 'Y' if removeWallpaper else 'N'
                decodedCustom['override-settings']['enable-remote-printer'] = 'Y' if enablePrinter else 'N'
                decodedCustom['override-settings']['enable-camera'] = 'Y' if enableCamera else 'N'
                decodedCustom['override-settings']['enable-terminal'] = 'Y' if enableTerminal else 'N'

            for line in defaultManual.splitlines():
                line = line.strip()
                if line and '=' in line:
                    k, value = line.split('=', 1)
                    decodedCustom['default-settings'][k.strip()] = value.strip()

            for line in overrideManual.splitlines():
                line = line.strip()
                if line and '=' in line:
                    k, value = line.split('=', 1)
                    decodedCustom['override-settings'][k.strip()] = value.strip()
            
            decodedCustomJson = json.dumps(decodedCustom)

            string_bytes = decodedCustomJson.encode("ascii")
            base64_bytes = base64.b64encode(string_bytes)
            encodedCustom = base64_bytes.decode("ascii")

            #github limits inputs to 10, so lump extras into one with json
            extras = {}
            extras['genurl'] = _settings.GENURL
            extras['runasadmin'] = runasadmin
            extras['urlLink'] = urlLink
            extras['downloadLink'] = downloadLink
            extras['delayFix'] = 'true' if delayFix else 'false'
            extras['version'] = version
            extras['rdgen'] = 'true'
            extras['cycleMonitor'] = 'true' if cycleMonitor else 'false'
            extras['xOffline'] = 'true' if xOffline else 'false'
            extras['hidecm'] = 'true' if hidecm else 'false'
            extras['removeNewVersionNotif'] = 'true' if removeNewVersionNotif else 'false'
            extras['compname'] = compname
            extra_input = json.dumps(extras)

            ####from here run the github action, we need user, repo, access token.
            if platform == 'windows':
                url = 'https://api.github.com/repos/'+_settings.GHUSER+'/'+_settings.REPONAME+'/actions/workflows/generator-windows.yml/dispatches'
            elif platform == 'windows-x86':
                url = 'https://api.github.com/repos/'+_settings.GHUSER+'/'+_settings.REPONAME+'/actions/workflows/generator-windows-x86.yml/dispatches'
            elif platform == 'linux':
                url = 'https://api.github.com/repos/'+_settings.GHUSER+'/'+_settings.REPONAME+'/actions/workflows/generator-linux.yml/dispatches'  
            elif platform == 'android':
                url = 'https://api.github.com/repos/'+_settings.GHUSER+'/'+_settings.REPONAME+'/actions/workflows/generator-android.yml/dispatches'
            elif platform == 'macos':
                url = 'https://api.github.com/repos/'+_settings.GHUSER+'/'+_settings.REPONAME+'/actions/workflows/generator-macos.yml/dispatches'
            else:
                url = 'https://api.github.com/repos/'+_settings.GHUSER+'/'+_settings.REPONAME+'/actions/workflows/generator-windows.yml/dispatches'

            #url = 'https://api.github.com/repos/'+_settings.GHUSER+'/rustdesk/actions/workflows/test.yml/dispatches'  
            data = {
                "ref":"master",
                "inputs":{
                    "server":server,
                    "key":key,
                    "apiServer":apiServer,
                    "custom":encodedCustom,
                    "uuid":myuuid,
                    "iconlink":iconlink,
                    "logolink":logolink,
                    "appname":appname,
                    "extras":extra_input,
                    "filename":filename
                }
            } 
            #print(data)
            headers = {
                'Accept':  'application/vnd.github+json',
                'Content-Type': 'application/json',
                'Authorization': 'Bearer '+_settings.GHBEARER,
                'X-GitHub-Api-Version': '2022-11-28'
            }
            create_github_run(myuuid,filename,platform)
            response = requests.post(url, json=data, headers=headers)
            print(response)
            if response.status_code == 204:
                #return render(request, 'waiting.html', {'filename':filename, 'uuid':myuuid, 'status':"Starting generator...please wait", 'phone_or_desktop': is_mobile(request), 'platform':platform})
                return HttpResponseRedirect('/api/clients')
            else:
                return JsonResponse({"error": "Something went wrong"})
    else:
        form = GenerateForm()
    return render(request, 'generator.html', {'form': form, 'phone_or_desktop': is_mobile(request)})

@login_required(login_url='/api/user_action?action=login')
def check_for_file(request):
    filename = request.GET['filename']
    uuid = request.GET['uuid']
    platform = request.GET['platform']
    gh_run = GithubRun.objects.filter(Q(uuid=uuid)).first()
    status = gh_run.status

    if status == "Success":
        #return render(request, 'generated.html', {'filename': filename, 'uuid':uuid, 'phone_or_desktop': is_mobile(request)})
        return HttpResponseRedirect('/api/clients')
    else:
        return render(request, 'waiting.html', {'filename':filename, 'uuid':uuid, 'status':status, 'platform':platform, 'phone_or_desktop': is_mobile(request)})

@login_required(login_url='/api/user_action?action=login')
def download_client(request):
    filename = request.GET['filename']
    uuid = request.GET['uuid']
    #filename = filename+".exe"
    file_path = os.path.join('exe',uuid,filename)
    with open(file_path, 'rb') as file:
        response = HttpResponse(file, headers={
            'Content-Type': 'application/vnd.microsoft.portable-executable',
            'Content-Disposition': f'attachment; filename="{filename}"'
        })

    return response

@login_required(login_url='/api/user_action?action=login')
def delete_pending(request):
    id = request.GET['id']
    pending = GithubRun.objects.get(id=id)
    pending.delete()
    return HttpResponseRedirect('/api/clients')

def save_png(file, uuid, domain, name):
    file_save_path = "png/%s/%s" % (uuid, name)
    Path("png/%s" % uuid).mkdir(parents=True, exist_ok=True)

    if isinstance(file, str):  # Check if it's a base64 string
        try:
            header, encoded = file.split(';base64,')
            decoded_img = base64.b64decode(encoded)
            file = ContentFile(decoded_img, name=name) # Create a file-like object
        except ValueError:
            print("Invalid base64 data")
            return None  # Or handle the error as you see fit
        except Exception as e:  # Catch general exceptions during decoding
            print(f"Error decoding base64: {e}")
            return None
        
    with open(file_save_path, "wb+") as f:
        for chunk in file.chunks():
            f.write(chunk)
    imageJson = {}
    imageJson['url'] = f"{domain}/api"
    imageJson['uuid'] = uuid
    imageJson['file'] = name
    #return "%s/%s" % (domain, file_save_path)
    return json.dumps(imageJson)

def get_png(request):
    filename = request.GET['filename']
    uuid = request.GET['uuid']
    #filename = filename+".exe"
    file_path = os.path.join('png',uuid,filename)
    with open(file_path, 'rb') as file:
        response = HttpResponse(file, headers={
            'Content-Type': 'application/vnd.microsoft.portable-executable',
            'Content-Disposition': f'attachment; filename="{filename}"'
        })

    return response


def create_github_run(myuuid, myname, myplatform):
    new_github_run = GithubRun(
        uuid=myuuid,
        status="Starting generator...please wait",
        name=myname,
        platform=myplatform
    )
    new_github_run.save()

def update_github_run(request):
    data = json.loads(request.body)
    myuuid = data.get('uuid')
    mystatus = data.get('status')
    GithubRun.objects.filter(Q(uuid=myuuid)).update(status=mystatus)
    return HttpResponse('')

def save_custom_client(request):
    file = request.FILES['file']
    myuuid = request.POST.get('uuid')
    
    # Validate UUID exists in database
    if not myuuid:
        return HttpResponse("Missing UUID", status=400)
    
    gh_run = GithubRun.objects.filter(Q(uuid=myuuid)).first()
    if not gh_run:
        print(f"Rejected file upload for invalid UUID: {myuuid}")
        return HttpResponse("Invalid UUID", status=403)
    
    # Sanitize filename to prevent path traversal and special characters
    safe_filename = os.path.basename(file.name)
    safe_filename = re.sub(r'[^A-Za-z0-9._-]', '_', safe_filename)
    
    # Save file locally with UUID-based path
    file_save_path = os.path.join("exe", myuuid, safe_filename)
    Path(os.path.join("exe", myuuid)).mkdir(parents=True, exist_ok=True)
    with open(file_save_path, "wb+") as f:
        for chunk in file.chunks():
            f.write(chunk)
    
    # Upload to GitHub releases
    try:
        upload_to_github_release(file_save_path, safe_filename, myuuid)
    except Exception as e:
        print(f"Failed to upload to GitHub releases: {e}")
    
    return HttpResponse("File saved successfully!")

def upload_to_github_release(file_path, filename, uuid):
    """Upload generated client to GitHub releases"""
    import datetime
    
    # Get metadata from GithubRun
    gh_run = GithubRun.objects.filter(Q(uuid=uuid)).first()
    if not gh_run:
        print(f"No GithubRun found for UUID {uuid}")
        return
    
    # Create release tag with timestamp
    timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    platform = gh_run.platform if hasattr(gh_run, 'platform') else 'unknown'
    release_tag = f"client-{platform}-{timestamp}"
    release_name = f"Custom Client - {gh_run.name if hasattr(gh_run, 'name') else filename}"
    
    # GitHub API headers
    headers = {
        'Accept': 'application/vnd.github+json',
        'Authorization': f'Bearer {_settings.GHBEARER}',
        'X-GitHub-Api-Version': '2022-11-28'
    }
    
    # Get the current repository (not rdgen)
    # We want to upload to the rustdesk-api-server repo, not rdgen
    if not _settings.GHUSER:
        print("GHUSER not configured, cannot upload to releases")
        return
    
    api_repo = os.environ.get('GITHUB_REPOSITORY', f'{_settings.GHUSER}/rustdesk-api-server')
    
    # Create release
    release_url = f'https://api.github.com/repos/{api_repo}/releases'
    release_data = {
        'tag_name': release_tag,
        'name': release_name,
        'body': f'Custom RustDesk client generated via API\n\nUUID: {uuid}\nPlatform: {platform}\nFilename: {filename}',
        'draft': False,
        'prerelease': False
    }
    
    response = requests.post(release_url, json=release_data, headers=headers)
    if response.status_code not in [200, 201]:
        print(f"Failed to create release: {response.status_code} - {response.text}")
        return
    
    release_id = response.json()['id']
    upload_url = response.json()['upload_url'].split('{')[0]
    
    # Upload file as release asset
    with open(file_path, 'rb') as f:
        file_data = f.read()
    
    upload_headers = headers.copy()
    upload_headers['Content-Type'] = 'application/octet-stream'
    
    asset_url = f"{upload_url}?name={quote(filename)}"
    response = requests.post(asset_url, data=file_data, headers=upload_headers)
    
    if response.status_code in [200, 201]:
        print(f"Successfully uploaded {filename} to release {release_tag}")
    else:
        print(f"Failed to upload asset: {response.status_code} - {response.text}")

def resize_and_encode_icon(imagefile):
    maxWidth = 200
    try:
        with io.BytesIO() as image_buffer:
            for chunk in imagefile.chunks():
                image_buffer.write(chunk)
            image_buffer.seek(0)

            img = Image.open(image_buffer)
            imgcopy = img.copy()
    except (IOError, OSError):
        raise ValueError("Uploaded file is not a valid image format.")

    # Check if resizing is necessary
    if img.size[0] <= maxWidth:
        with io.BytesIO() as image_buffer:
            imgcopy.save(image_buffer, format=imagefile.content_type.split('/')[1])
            image_buffer.seek(0)
            return_image = ContentFile(image_buffer.read(), name=imagefile.name)
        return base64.b64encode(return_image.read())

    # Calculate resized height based on aspect ratio
    wpercent = (maxWidth / float(img.size[0]))
    hsize = int((float(img.size[1]) * float(wpercent)))

    # Resize the image while maintaining aspect ratio using LANCZOS resampling
    imgcopy = imgcopy.resize((maxWidth, hsize), Image.Resampling.LANCZOS)

    with io.BytesIO() as resized_image_buffer:
        imgcopy.save(resized_image_buffer, format=imagefile.content_type.split('/')[1])
        resized_image_buffer.seek(0)

        resized_imagefile = ContentFile(resized_image_buffer.read(), name=imagefile.name)

    # Return the Base64 encoded representation of the resized image
    resized64 = base64.b64encode(resized_imagefile.read())
    #print(resized64)
    return resized64


def is_mobile(request):
    user_agent = request.META['HTTP_USER_AGENT']
    if 'Mobile' in user_agent or 'Android' in user_agent or 'iPhone' in user_agent:
        return 'base_phone.html'
    else:
        return 'base.html'