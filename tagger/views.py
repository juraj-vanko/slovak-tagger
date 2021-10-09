from warnings import catch_warnings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.mixins import UpdateModelMixin, DestroyModelMixin

from .models import Sentence
from .serializers import TodoSerializer, YourSerializer

import stanza
import json
from .dictionaries import xpos

class TaggerView(
  APIView, # Basic View class provided by the Django Rest Framework
  UpdateModelMixin, # Mixin that allows the basic APIView to handle PUT HTTP requests
  DestroyModelMixin, # Mixin that allows the basic APIView to handle DELETE HTTP requests
):

  def get(self, request, id=None):
    nlp = stanza.Pipeline(lang="sk")
    veta = request.GET['sentence']
    dokument = nlp(veta)
    tagsdb = json.load(open("./static/tags.json", encoding="utf8"))
    schema = json.load(open("./static/sentence-schema.json", encoding="utf8"))
    print(tagsdb['S']['tags']['2']['label'])
    """if id:
      # If an id is provided in the GET request, retrieve the Todo item by that id
      try:
        # Check if the todo item the user wants to update exists
        queryset = Todo.objects.get(id=id)
      except Todo.DoesNotExist:
        # If the todo item does not exist, return an error response
        return Response({'errors': 'This todo item does not exist.'}, status=400)

      # Serialize todo item from Django queryset object to JSON formatted data
      read_serializer = TodoSerializer(queryset)

    else:
      # Get all todo items from the database using Django's model ORM
      queryset = Todo.objects.all()

      # Serialize list of todos item from Django queryset object to JSON formatted data
      read_serializer = TodoSerializer(queryset, many=True)

    # Return a HTTP response object with the list of todo items as JSON
    """
    tokenized = []
    print(dokument)

    for vety in dokument.sentences:
        for slovo in vety.words:

            wordType = {}
            recTags = []
            for i, tag in enumerate(slovo.xpos):

                if i == 0:
                    wordType = {
                        'label': tagsdb[slovo.xpos[0]]['label'],
                        'slovakName': tagsdb[slovo.xpos[0]]['slovakName'],
                        'color': tagsdb[slovo.xpos[0]]['color'],
                    }

                else:
                    if bool(tagsdb[slovo.xpos[0]]['tags']):
                        if ":" == slovo.xpos[i]:
                            if ":r" == slovo.xpos[i:i+2]:
                                print("toto je vyjebaný integer",slovo.xpos[i:i+2])
                                recTags.append(
                                    {
                                    'label': 'Informácia',
                                    'value': 'Vlastné meno'
                                    }
                                )
                                break

                            else:
                                recTags.append(
                                    {
                                    'label': 'Informácia',
                                    'value': 'Chybný zápis'
                                    }
                                )   
                                break   

                        else:
                            recTags.append(
                                {
                                    'label': tagsdb[slovo.xpos[0]]['tags'][tag]['label'],
                                    'value': tagsdb[slovo.xpos[0]]['tags'][tag]['value']
                                }
                            )

            print(wordType)
            print(recTags)
            tokenized.append(
                {
                    'id': slovo.id,
                    'word': slovo.text,
                    'lemma': slovo.lemma,
                    'head': str(slovo.head),
                    'xpos': slovo.xpos,
                    'deprel': slovo.deprel,                    
                    'schema': schema[slovo.deprel],
                    'wordtype': wordType,
                    'tags': recTags
                }
            )                    

    yourdata= [{"tagger": tokenized}]
    results = YourSerializer(yourdata, many=True).data

    return Response(results)


  def post(self, request):
    # Pass JSON data from user POST request to serializer for validation
    create_serializer = TodoSerializer(data=request.data)

    # Check if user POST data passes validation checks from serializer
    if create_serializer.is_valid():

      # If user data is valid, create a new todo item record in the database
      todo_item_object = create_serializer.save()

      # Serialize the new todo item from a Python object to JSON format
      read_serializer = TodoSerializer(todo_item_object)

      # Return a HTTP response with the newly created todo item data
      return Response(read_serializer.data, status=201)

    # If the users POST data is not valid, return a 400 response with an error message
    return Response(create_serializer.errors, status=400)


  def put(self, request, id=None):
    try:
      # Check if the todo item the user wants to update exists
      todo_item = Sentence.objects.get(id=id)
    except Sentence.DoesNotExist:
      # If the todo item does not exist, return an error response
      return Response({'errors': 'This todo item does not exist.'}, status=400)

    # If the todo item does exists, use the serializer to validate the updated data
    update_serializer = TodoSerializer(todo_item, data=request.data)

    # If the data to update the todo item is valid, proceed to saving data to the database
    if update_serializer.is_valid():

      # Data was valid, update the todo item in the database
      todo_item_object = update_serializer.save()

      # Serialize the todo item from Python object to JSON format
      read_serializer = TodoSerializer(todo_item_object)

      # Return a HTTP response with the newly updated todo item
      return Response(read_serializer.data, status=200)

    # If the update data is not valid, return an error response
    return Response(update_serializer.errors, status=400)


  def delete(self, request, id=None):
    try:
      # Check if the todo item the user wants to update exists
      todo_item = Sentence.objects.get(id=id)
    except Sentence.DoesNotExist:
      # If the todo item does not exist, return an error response
      return Response({'errors': 'This todo item does not exist.'}, status=400)

    # Delete the chosen todo item from the database
    todo_item.delete()

    # Return a HTTP response notifying that the todo item was successfully deleted
    return Response(status=204)