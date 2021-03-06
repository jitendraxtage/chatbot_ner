import json
from django.http import HttpResponse
from datastore.datastore import DataStore
from datastore.exceptions import (DataStoreSettingsImproperlyConfiguredException, EngineNotImplementedException,
                                  EngineConnectionException, IndexForTransferException,
                                  AliasForTransferException, NonESEngineTransferException)
from datastore.exceptions import IndexNotFoundException, InvalidESURLException, \
    SourceDestinationSimilarException, \
    InternalBackupException, AliasNotFoundException, PointIndexToAliasException, \
    FetchIndexForAliasException, DeleteIndexFromAliasException
from chatbot_ner.config import ner_logger
from external_api.constants import ENTITY_DATA, ENTITY_NAME, LANGUAGE_SCRIPT, ENTITY_LIST, EXTERNAL_API_DATA
from django.views.decorators.csrf import csrf_exempt


def get_entity_word_variants(request):
    """
    This function is used obtain the entity dictionary given the dictionary name.
    Args:
        request (HttpResponse): HTTP response from url

    Returns:
        HttpResponse : With data consisting of a list of value variants.
    """
    response = {"success": False, "error": "", "result": []}
    try:
        entity_name = request.GET.get(ENTITY_NAME)
        datastore_obj = DataStore()
        result = datastore_obj.get_entity_dictionary(entity_name=entity_name)

        structured_result = []
        # The list around result.keys() is to make it compatible to python3
        key_list = list(result.keys())
        key_list.sort()
        for value in key_list:
            structured_result.append({'value': value, 'variants': result[value]})
        result = structured_result

        response['result'] = result
        response['success'] = True

    except (DataStoreSettingsImproperlyConfiguredException,
            EngineNotImplementedException,
            EngineConnectionException, FetchIndexForAliasException) as error_message:
        response['error'] = str(error_message)
        ner_logger.exception('Error: %s' % error_message)
        return HttpResponse(json.dumps(response), content_type='application/json', status=500)

    except BaseException as e:
        response['error'] = str(e)
        ner_logger.exception('Error: %s' % e)
        return HttpResponse(json.dumps(response), content_type='application/json', status=500)

    return HttpResponse(json.dumps(response), content_type='application/json', status=200)


@csrf_exempt
def update_dictionary(request):
    """
    This function is used to update the dictionary entities.
    Args:
        request (HttpResponse): HTTP response from url

    Returns:
        HttpResponse : HttpResponse with appropriate status and error message.
    """
    response = {"success": False, "error": ""}
    try:
        external_api_data = json.loads(request.POST.get(EXTERNAL_API_DATA))
        entity_name = external_api_data.get(ENTITY_NAME)
        entity_data = external_api_data.get(ENTITY_DATA)
        language_script = external_api_data.get(LANGUAGE_SCRIPT)
        datastore_obj = DataStore()
        datastore_obj.update_entity_data(entity_name=entity_name,
                                         entity_data=entity_data,
                                         language_script=language_script)
        response['success'] = True

    except (DataStoreSettingsImproperlyConfiguredException,
            EngineNotImplementedException,
            EngineConnectionException, FetchIndexForAliasException) as error_message:
        response['error'] = str(error_message)
        ner_logger.exception('Error: %s' % error_message)
        return HttpResponse(json.dumps(response), content_type='application/json', status=500)

    except BaseException as e:
        response['error'] = str(e)
        ner_logger.exception('Error: %s' % e)
        return HttpResponse(json.dumps(response), content_type='application/json', status=500)
    return HttpResponse(json.dumps(response), content_type='application/json', status=200)


@csrf_exempt
def transfer_entities(request):
    """
    This method is used to transfer entities from the source to destination.
    Args:
        request (HttpResponse): HTTP response from url
    Returns:
        HttpResponse : HttpResponse with appropriate status and error message.
    """
    response = {"success": False, "error": ""}
    try:
        external_api_data = json.loads(request.POST.get(EXTERNAL_API_DATA))
        entity_list = external_api_data.get(ENTITY_LIST)

        datastore_object = DataStore()
        datastore_object.transfer_entities_elastic_search(entity_list=entity_list)
        response['success'] = True

    except (IndexNotFoundException, InvalidESURLException,
            SourceDestinationSimilarException, InternalBackupException, AliasNotFoundException,
            PointIndexToAliasException, FetchIndexForAliasException, DeleteIndexFromAliasException,
            AliasForTransferException, IndexForTransferException, NonESEngineTransferException) as error_message:
        response['error'] = str(error_message)
        ner_logger.exception('Error: %s' % error_message)
        return HttpResponse(json.dumps(response), content_type='application/json', status=500)

    except BaseException as e:
        response['error'] = str(e)
        ner_logger.exception('Error: %s' % e)
        return HttpResponse(json.dumps(response), content_type='application/json', status=500)

    return HttpResponse(json.dumps(response), content_type='application/json', status=200)
