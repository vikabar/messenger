from messenger.models import Message
from messenger.serializers import *
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
import json


class MessageList(APIView):
    status_dict = {"success": "succsess", "error": "error"}

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
                    dict = {"status" : self.status_dict["success"], "data" : serializer.data}
                    return Response(dict, status=status.HTTP_200_OK)
                except:
                    return Response("Oooops, the message doesn't exist or you dont have permission to read it. Please check the id you've entered",
                                    status=status.HTTP_400_BAD_REQUEST)

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
                return Response("Oooops, Something wrong with your request params", status=status.HTTP_400_BAD_REQUEST)

            serializer = MessageSerializer(res, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except:
            return Response("Oooops, Something went wrong. Please try again", status=status.HTTP_400_BAD_REQUEST)
    '''
    posting new message by logged-in user.
    mandatory params: email(of existing user), message_subject
    optional params: message_body (it the request doesn't have this param - the message body will be empty
    '''
    def post(self, request):
        try:
            sender = request.user
            email = request.GET.get(('email'), None)
            message_body = request.GET.get('message_body', "")
            message_subject = request.GET.get('message_subject', None)

            # mail and message subject are mandatory params. The request Must contain them
            if None in [email, message_subject]:
                return Response("Oooops, Something wrong with your request params", status=status.HTTP_400_BAD_REQUEST)

            # the email belongs to EXISTING user
            try:
                receiver = User.objects.get(email=email)
            except:
                return Response("Oooops, the recepient doesn't exist. Please check the email you've entered", status=status.HTTP_400_BAD_REQUEST)

            message = Message()
            message.message_body = message_body
            message.message_subject = message_subject
            message.sender = sender
            message.receiver = receiver
            message.save()
            return Response("The message was created successfully", status=status.HTTP_201_CREATED)
        except:
            return Response("Oooops, Something went wrong. Please try again", status=status.HTTP_400_BAD_REQUEST)

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
                return Response("Oooops, the message doesn't exist. Please check the id you've entered",
                                status=status.HTTP_400_BAD_REQUEST)
            update_type = request.GET.get('update_type', None)
            if update_type is None:
                return Response("Oooops, the message must contain an update type. Please correct your request",
                                status=status.HTTP_400_BAD_REQUEST)

            # the sender deletes message FROM HIS LOG
            if user == msg.sender:
                print("111111dxx111111111111")
                if update_type == "delete":
                    msg.mark_deleted_by_sender()
                    return Response("The message was deleted from sender's log", status=status.HTTP_200_OK)
                else:
                    return Response("The user only allowed to delete this message", status=status.HTTP_403_FORBIDDEN)

            elif user == msg.receiver:
                # the recepient deletes the message FROM HIS LOG
                if update_type == "delete":
                    msg.mark_deleted_by_receiver()
                    return Response("the message was deleted from recepient's log", status=status.HTTP_200_OK)

                # the recepient marks message as read
                elif update_type == "mark_read":
                    msg.mark_read()
                    return Response("the message was read by the user", status=status.HTTP_200_OK)
            else:
                return Response("The user is not authorized to update this message. Make sure that the update tipe match your permissions", status=status.HTTP_403_FORBIDDEN)

        except:
            return Response("Oooops, Something went wrong. Please try again", status=status.HTTP_400_BAD_REQUEST)
