from warnings import catch_warnings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.mixins import UpdateModelMixin, DestroyModelMixin

from .serializers import YourSerializer

import stanza
import json
from .dictionaries import xpos

class TaggerView(
  APIView, # Mixin, ktorý umožňuje základnému APIView spracovávať DELETE HTTP požiadavky
  UpdateModelMixin, # Mixin, ktorý umožňuje základnému APIView spracovávať požiadavky PUT HTTP
  DestroyModelMixin, # Mixin, ktorý umožňuje základnému APIView spracovávať DELETE HTTP požiadavky
):

  def get(self, request, id=None):
    nlp = stanza.Pipeline(lang="sk", verbose=False)
    veta = request.GET['sentence']
    dokument = nlp(veta)
    tagsdb = json.load(open("./static/tags.json", encoding="utf8"))
    schema = json.load(open("./static/sentence-schema.json", encoding="utf8"))
    tokenized = []

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