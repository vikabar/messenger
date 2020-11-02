from messenger.models import Message
from messenger.serializers import *
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
import json


class MessageList(APIView):
    status_dict = {"success": "Succsess", "error": "Error"}

    '''
    list of messages for logged-in user: unread(received)/sent/received/all. The response will contain only messages that were not deleted by the user
    params: unread=true, type=all, type=sent, type=received
    '''
    def get(self, request):
        try:
            user = request.user
            msg_id = request.GET.get('msg_id', None)
            #read received message
            if msg_id is not None:
                try:
                    msg = Message.objects.get(pk=request.GET.get('msg_id'), receiver=user, is_deleted_by_receiver=False)
                    serializer = MessageSerializer(msg)
                    msg.mark_read()
                    dict = {"Status" : self.status_dict["success"], "Message": "", "data" : serializer.data}
                    return Response(dict, status=status.HTTP_200_OK)
                except:
                    dict = {"Status" : self.status_dict["error"], "Message" : "Invalid message ID or user dont have permission to read it", "data": ""}
                    return Response(dict, status=status.HTTP_200_OK)

            unread = request.GET.get('unread', None)
            type = request.GET.get('type', None)

            #unread messages received by the user
            if unread is not None and unread == "true":
                res = Message.objects.filter(receiver = user).filter(is_deleted_by_receiver=False).filter(is_read=False)

            #all messages sent OR received by the user
            elif type == "all":
                res = Message.objects.filter(receiver =user) | Message.objects.filter(sender = user).filter(is_deleted_by_sender=False).filter(is_deleted_by_receiver=False)

            # all messages sent
            elif type == "sent":
                res = Message.objects.filter(sender = user).filter(is_deleted_by_sender=False)

            # all messages received by the user
            elif type == "received":
                res = Message.objects.filter(receiver =user).filter(is_deleted_by_receiver=False)

            else:
                return Response("Bad request", status=status.HTTP_400_BAD_REQUEST)

            serializer = MessageSerializer(res, many=True)
            dict = {"Status" : self.status_dict["success"], "Message": "", "data" : serializer.data}
            return Response(dict, status=status.HTTP_200_OK)

        except:
            return Response("Bad request", status=status.HTTP_400_BAD_REQUEST)
    '''
    posting new message by logged-in user.
    mandatory params: email(of existing user), message_subject
    optional params: message_body (it the request doesn't have this param - the message body will be empty
    '''
    def post(self, request):
        try:
            sender = request.user
            body_unicode = request.body.decode('utf-8')

            body = json.loads(body_unicode)
            message_body = ""
            message_subject = ""
            email = ""
            if "message_body" in body:
                message_body = body["message_body"]

            if "message_subject" in body:
                message_subject = body["message_subject"]

            if "email" in body:
                email = body["email"]


            # mail and message subject are mandatory params. The request Must contain them
            if email == "":
                dict = {"Status": self.status_dict["error"], "Message": "Missing email address"}
                return Response(dict, status=status.HTTP_200_OK)

            # the email belongs to EXISTING user
            try:
                receiver = User.objects.get(email=email)
            except:
                dict = {"Status": self.status_dict["error"], "Message": "The recepient doesn't exist"}
                return Response(dict, status=status.HTTP_200_OK)

            message = Message()
            message.message_body = message_body
            message.message_subject = message_subject
            message.sender = sender
            message.receiver = receiver
            message.save()
            dict = {"Status": self.status_dict["success"], "Message": ""}
            return Response(dict, status=status.HTTP_201_CREATED)
        except:
            return Response("Bad request", status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    '''
    updating specific message. The recepient can mark his mail as read.
    Both the sender and the recepient can delete the message FROM THEIR LOG
    params:msg_id (the primary key of the message), type of update: update_type=delete, update_type=mark_read
    '''
    def put(self, request):
        try:
            user = request.user
            try:
                msg = Message.objects.get(pk=request.GET.get('msg_id'))
            except:
                dict = {"Status": self.status_dict["error"], "Message": "Invalid message id"}
                return Response(dict, status=status.HTTP_200_OK)
            update_type = request.GET.get('update_type', None)
            if update_type is None:
                return Response("Bad request", status=status.HTTP_400_BAD_REQUEST)

            if user == msg.receiver:
                if not msg.is_deleted_by_receiver:
                    # the recepient deletes the message FROM HIS LOG
                    if update_type == "delete":
                        msg.mark_deleted_by_receiver()
                        dict = {"Status": self.status_dict["success"], "Message": ""}
                        return Response(dict, status=status.HTTP_200_OK)

                    # the recepient marks message as read
                    elif update_type == "mark_read":
                        msg.mark_read()
                        dict = {"Status": self.status_dict["success"], "Message": ""}
                        return Response(dict, status=status.HTTP_200_OK)

                    else:
                        dict = {"Status": self.status_dict["error"], "Message": "Invalid request"}
                        return Response(dict, status=status.HTTP_200_OK)
                else:
                    dict = {"Status": self.status_dict["error"], "Message": "Invalid request"}
                    return Response(dict, status=status.HTTP_200_OK)

            # the sender deletes message FROM HIS LOG
            elif user == msg.sender:
                if not msg.is_deleted_by_sender:
                    if update_type == "delete":
                        msg.mark_deleted_by_sender()
                        dict = {"Status": self.status_dict["success"], "Message": ""}
                        return Response(dict, status=status.HTTP_200_OK)
                    else:
                        dict = {"Status": self.status_dict["error"], "Message": "Invalid request"}
                        return Response(dict, status=status.HTTP_200_OK)
                else:
                    dict = {"Status": self.status_dict["error"], "Message": "Invalid request"}
                    return Response(dict, status=status.HTTP_200_OK)
            else:
                dict = {"Status": self.status_dict["error"], "Message": "Invalid request"}
                return Response(dict, status=status.HTTP_200_OK)

        except:
            return Response("Bad request", status=status.HTTP_500_INTERNAL_SERVER_ERROR)
