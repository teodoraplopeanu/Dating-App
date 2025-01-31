from calendar import month
from datetime import datetime

from django.shortcuts import render, HttpResponse, redirect
from ..utils import *
from ..models import User, UserImage, Gender, addUserLike, getChatRoom, getChatRooms, getMatchesForUser, unmatchUser, \
    getMatch
from ..messaging import *
import logging
import base64
import json
import uuid

logger = logging.getLogger(__name__)


def userEditView(request):
    try:
        jwt_token_decoder = JWTTokenDecoder(request)
        user = jwt_token_decoder.getUserFromToken()

        if user is None:
            return redirect("login")

        images = user.getImagesList()
        user_age = user.calculateAge()

        return render(request, "user/edit.html", {"user": user, "images": images, "age": user_age})
    except:
        return redirect("login")


# POST api/user/edit/ - body -
# {'gender' : gender,
# 'genderPreference': gp,
# 'description': d
# ... other fields}
def userEdit(request):
    try:
        jwt_token_decoder = JWTTokenDecoder(request)
        user = jwt_token_decoder.getUserFromToken()

        if user is None:
            return redirect("login")

        userQuery = User.objects.filter(user_id=user.user_id)

        if request.POST['description'] != "":
            userQuery.update(
                description_encoded_64=base64.b64encode(request.POST['description'].encode("utf-8")).decode("utf-8"))

        if request.POST['gender'] != "":
            userQuery.update(
                gender=request.POST['gender'])

        if request.POST['genderPreference'] != "":
            userQuery.update(
                gender_preference=request.POST['genderPreference'])

        response = {'status': 'success'}
        return HttpResponse(json.dumps(response), content_type="application/json")
    except Exception as e:
        logger.error(e)
        return redirect("login")


# POST - api/user/edit/photo/ - file body -> image
def userEditPhoto(request):
    try:
        jwt_token_decoder = JWTTokenDecoder(request)
        user = jwt_token_decoder.getUserFromToken()

        if user is None:
            return redirect("login")

        noPhotos = user.images.all().count()

        if noPhotos >= 4:
            response = {'error': "Can't add more than 4 photos."}
            return HttpResponse(json.dumps(response), content_type="application/json")

        if 'file' not in request.FILES:
            response = {'error': "No photo uploaded."}
            return HttpResponse(json.dumps(response), content_type="application/json")

        filename = 'rizzder_app/files/user_images/tmp-' + str(uuid.uuid4())

        with open(filename, "wb+") as file:
            file.write(request.FILES['file'].read())
            file.flush()
            userImage = UserImage.objects.create(active=True, image=filename)
            userImage.save()
            user.images.add(userImage)
            user.save()

            if noPhotos == 0:
                user.profile_image_id = user.getFirstImageId()
                user.save()

        response = {'status': 'success'}
        return HttpResponse(json.dumps(response), content_type="application/json")
    except Exception as e:
        logger.error(e)
        return redirect("login")


# POST - api/user/edit/delete/photo/ - {'id' : image_id}
def userDeletePhoto(request):
    try:
        jwt_token_decoder = JWTTokenDecoder(request)
        user = jwt_token_decoder.getUserFromToken()

        if user is None:
            return redirect("login")

        image_id = int(request.POST['id'])
        UserImage.objects.filter(user_image_id=image_id).delete()

        noPhotos = user.images.all().count()
        if noPhotos == 0:
            user.profile_image_id = 0
            user.save()
        else:
            if user.profile_image_id == image_id:
                user.profile_image_id = user.getFirstImageId()
                user.save()
        response = {'status': 'success'}
        return HttpResponse(json.dumps(response), content_type="application/json")
    except Exception as e:
        logger.error(e)
        return redirect("login")


# GET - api/user/genders/
def getGenders(request):
    try:
        jwt_token_decoder = JWTTokenDecoder(request)
        user = jwt_token_decoder.getUserFromToken()

        if user is None:
            return redirect("login")

        genders = [{"key": e.value, "value": e.name} for e in Gender]

        response = {'status': 'success', "genders": genders}
        return HttpResponse(json.dumps(response), content_type="application/json")
    except Exception as e:
        logger.error(e)
        return redirect("login")


# GET - api/user/info/getLocation/
def getUserLocation(request):
    try:
        jwt_token_decoder = JWTTokenDecoder(request)
        user = jwt_token_decoder.getUserFromToken()

        if user is None:
            return redirect("login")

        remote_addr = request.META.get('HTTP_X_FORWARDED_FOR')
        if remote_addr:
            address = remote_addr.split(',')[-1].strip()
        else:
            address = request.META.get('REMOTE_ADDR')

        location = Location(address)
        lat, lon = location.getLatitudeAndLongitude()

        userQuery = User.objects.filter(user_id=user.user_id)
        userQuery.update(latitude=lat, longitude=lon)
        response = {'status': 'success'}
        return HttpResponse(json.dumps(response), content_type="application/json")
    except Exception as e:
        logger.error(e)
        return redirect("login")


def userMeetView(request):
    try:
        jwt_token_decoder = JWTTokenDecoder(request)
        user = jwt_token_decoder.getUserFromToken()

        if user is None:
            return redirect("login")

        return render(request, "user/meet.html");
    except Exception as e:
        logger.error(e)
        return redirect("login")


# GET - api/user/getPreferredUsers/
def getPreferredUsers(request):
    try:
        jwt_token_decoder = JWTTokenDecoder(request)
        user = jwt_token_decoder.getUserFromToken()

        if user is None:
            return redirect("login")

        response = {'status': 'success', 'users': User.getPreferredUsers(user, 5)}
        return HttpResponse(json.dumps(response), content_type="application/json")
    except Exception as e:
        logger.error(e)
        return redirect("login")


# POST api/user/meet/like/ - body - {'receiver_id' : id, 'like': t/f (like/reject)}
def likeUser(request):
    try:
        jwt_token_decoder = JWTTokenDecoder(request)
        user = jwt_token_decoder.getUserFromToken()

        if user is None:
            return redirect("login")

        receiverID = request.POST['receiver_id']
        receiver = User.objects.get(user_id=receiverID)

        if receiver is None:
            return HttpResponse(json.dumps({'status': 'failed', 'message': 'Receiver user not found!'}),
                                content_type="application/json")

        matched = addUserLike(user, receiver, request.POST['like'])

        logger.info(matched)

        if matched is None:
            return HttpResponse(json.dumps({'error': "Couldn't like user"}), content_type="application/json")
        return HttpResponse(json.dumps({'status': 'success', 'matched': matched}), content_type="application/json")
    except Exception as e:
        logger.error(e)
        return redirect("login")


# POST api/user/block/ - body - {'receiver_id' : id}
def blockUser(request):
    try:
        jwt_token_decoder = JWTTokenDecoder(request)
        user = jwt_token_decoder.getUserFromToken()

        if user is None:
            return redirect("login")

        receiverID = request.POST['receiver_id']
        receiver = User.objects.get(user_id=receiverID)

        if receiver is None:
            return HttpResponse(json.dumps({'status': 'failed', 'message': 'Receiver user not found!'}),
                                content_type="application/json")

        user.blockUser(receiver)
        return HttpResponse(json.dumps({'status': 'success'}), content_type="application/json")
    except Exception as e:
        logger.error(e)
        return redirect("login")


# POST api/user/unblock/ - body - {'receiver_id' : id}
def unblockUser(request):
    try:
        jwt_token_decoder = JWTTokenDecoder(request)
        user = jwt_token_decoder.getUserFromToken()

        if user is None:
            return redirect("login")

        receiverID = request.POST['receiver_id']
        receiver = User.objects.get(user_id=receiverID)

        if receiver is None:
            return HttpResponse(json.dumps({'status': 'failed', 'message': 'Receiver user not found!'}),
                                content_type="application/json")

        user.unblockUser(receiver)
        return HttpResponse(json.dumps({'status': 'success'}), content_type="application/json")
    except Exception as e:
        logger.error(e)
        return redirect("login")


# POST api/user/setGhosted/ - body - {'receiver_id' : id, 'block_receiver': t/f}
def setGhosted(request):
    try:
        jwt_token_decoder = JWTTokenDecoder(request)
        user = jwt_token_decoder.getUserFromToken()

        if user is None:
            return redirect("login")

        receiverID = request.POST['receiver_id']
        receiver = User.objects.get(user_id=receiverID)

        if receiver is None:
            return HttpResponse(json.dumps({'status': 'failed', 'message': 'Receiver user not found!'}),
                                content_type="application/json")

        if getMatch(user, receiver):
            unmatchUser(user, receiver, request.POST['block_receiver'])
            user.changeScore(-200)
        return HttpResponse(json.dumps({'status': 'success'}), content_type="application/json")
    except Exception as e:
        logger.error(e)
        return redirect("login")


def chatRoomView(request):
    try:
        jwt_token_decoder = JWTTokenDecoder(request)
        user = jwt_token_decoder.getUserFromToken()

        if user is None:
            return redirect("login")

        receiverUser = User.objects.get(user_id=request.GET['receiver_user_id'])
        if receiverUser is None:
            return redirect("login")

        (chatRoom, messages) = getChatRoom(chatName([user, receiverUser]))

        noMessages = len(messages)
        ghosted = False
        if noMessages > 0:
            lastMessage = messages[noMessages - 1]
            if lastMessage.user_sender.all()[0].user_id == user.user_id:
                if currentTimeMillis() - lastMessage.date >= 1000 * 60 * 60 * 24 * 7:
                    ghosted = True

        timeArray = []
        for message in messages:
            hour = (message.date / (1000 * 60 * 60) + 2) % 24
            minute = message.date / (1000 * 60) % 60

            formatedTime = ""

            if hour < 10:
                formatedTime += "0" + str(int(hour)) + ":"
            else:
                formatedTime += str(int(hour)) + ":"

            if minute < 10:
                formatedTime += "0" + str(int(minute))
            else:
                formatedTime += str(int(minute))

            timeArray.append(formatedTime)

        dateArray = []
        for message in messages:
            # Convert the timestamp to a datetime object
            dt_object = datetime.fromtimestamp(message.date / 1000)

            # Format the datetime object as 'day.month.year'
            formatted_date = dt_object.strftime('%d.%m.%Y')

            dateArray.append(formatted_date)

        for i in range(len(messages) - 1, 0, -1):
            if dateArray[i] == dateArray[i - 1]:
                dateArray[i] = ""

        dt_object = datetime.fromtimestamp(user.last_online / 1000)
        formated_date = dt_object.strftime('%d.%m.%Y')

        last_online = ""
        if currentTimeMillis() - receiverUser.last_online < 1000:
            last_online = currentTimeMillis() - user.last_online
        elif formated_date != datetime.now().strftime('%d.%m.%Y'):
            last_online = "Last seen on " + formated_date
        else:
            hour = (receiverUser.last_online / (1000 * 60 * 60) + 2) % 24
            minute = receiverUser.last_online / (1000 * 60) % 60
            last_online = "Last seen today at "

            if hour < 10:
                last_online += "0" + str(int(hour)) + ":"
            else:
                last_online += str(int(hour)) + ":"

            if minute < 10:
                last_online += "0" + str(int(minute))
            else:
                last_online += str(int(minute))


        return render(request, "user/chatRoom.html",
                      context={'user': user,
                               'receiverUser': receiverUser,
                               'roomName': chatName([user, receiverUser]),
                               'array': zip(messages, timeArray, dateArray),
                               'last_online': last_online,
                               'chatRoom': chatRoom,
                               'messages': messages,
                               'ghosted': ghosted})
    except Exception as e:
        logger.error(e)
        return redirect("login")


def getChatRoomsView(request):
    try:
        jwt_token_decoder = JWTTokenDecoder(request)
        user = jwt_token_decoder.getUserFromToken()

        last_time_array = []
        for chatRoom in getChatRooms(user):
            last_message = chatRoom['last_message']

            if last_message is None:
                last_time_array.append("")
                continue

            hour = (last_message.date / (1000 * 60 * 60) + 2) % 24
            minute = last_message.date / (1000 * 60) % 60

            dt_object = datetime.fromtimestamp(last_message.date / 1000)
            formated_date = dt_object.strftime('%d.%m.%Y')

            if formated_date != datetime.now().strftime('%d.%m.%Y'):
                last_time_array.append(formated_date)
            else:
                formated_time = ""
                if hour < 10:
                    formated_time += "0" + str(int(hour)) + ":"
                else:
                    formated_time += str(int(hour)) + ":"

                if minute < 10:
                    formated_time += "0" + str(int(minute))
                else:
                    formated_time += str(int(minute))

                last_time_array.append(formated_time)

        if user is None:
            return redirect("login")

        logger.info(getChatRooms(user))

        matches = getMatchesForUser(user)
        logger.info(matches)


        chats = getChatRooms(user)

        remove_matches = []
        for match in matches:
            for CHAT in chats:
                if match['user_id'] == CHAT['user'].user_id:
                    remove_matches.append(match)
                if match["user_id"] == user.user_id:
                    remove_matches.append(match)

        for match in remove_matches:
            matches.remove(match)

        return render(request, "user/chatRooms.html",
                      context={'user': user,
                               'matches': matches,
                               'array': zip(chats, last_time_array),})
    except Exception as e:
        logger.error(e)
        return redirect("login")

def getMatches(request):
    try:
        jwt_token_decoder = JWTTokenDecoder(request)
        user = jwt_token_decoder.getUserFromToken()

        if user is None:
            return redirect("login")
        logger.info(getMatchesForUser(user))
        return HttpResponse(json.dumps({'status': 'success', 'users': getMatchesForUser(user)}),
                            content_type="application/json")
    except Exception as e:
        logger.error(e)
        return redirect("login")


# POST - api/user/edit/photo/changeProfileImage - {'image_id' : id}
def changeProfileImage(request):
    try:
        jwt_token_decoder = JWTTokenDecoder(request)
        user = jwt_token_decoder.getUserFromToken()

        if user is None:
            return redirect("login")

        image_id = request.POST['image_id']
        if user.imageExists(image_id):
            user.profile_image_id = image_id
            user.save()
            return HttpResponse(json.dumps({'status': 'success'}),
                                content_type="application/json")
        else:
            return HttpResponse(json.dumps({'status': 'error', 'error': 'Image does not exist!'}),
                                content_type="application/json")
    except Exception as e:
        logger.error(e)
        return redirect("login")
