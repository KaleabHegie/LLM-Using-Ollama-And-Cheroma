from django.shortcuts import render, HttpResponse
from django.http import JsonResponse , StreamingHttpResponse
from rest_framework import status
from .ollama_doc_init import chain
from django.views.decorators.csrf import csrf_exempt
from asgiref.sync import sync_to_async
import asyncio
from .models import QuestionHistory
import json
import markdown   

async def ask_questions(request):
    """
    Handles both POST (question submission) and GET (server-sent events) methods.
    """

    if request.method == 'POST':
        
        question = request.POST.get('question', '').strip()
        try:
             # Convert to sync to perform ORM operations
              created_obj = await sync_to_async(QuestionHistory.objects.create)(
                 question=question,
                 user=request.user
             )
              created_obj_id = created_obj.id
        except Exception as e:
             return JsonResponse({"error": f"Failed to save question: {str(e)}"}, status=500)

       
    
        if not question:
            return JsonResponse({"error": "Question not provided"}, status=400)

        # # Simulating async task
        await asyncio.sleep(0.1)

        # # Return a JSON response
        return JsonResponse({"status": "ok", "message": f"Query '{question}' received" , "obj_id" : created_obj_id })

    elif request.method == 'GET':
        async def event_stream():
            try:
                # Simulate streaming response
                last_question_obj = await sync_to_async(QuestionHistory.objects.last)()
                if last_question_obj:
                    query = last_question_obj.question
                    try:
                        response_data = ''
                        for chunk in chain.stream(query):  # Pass query as a string
                           formatted_chunk = json.dumps({"chunk" : chunk })
                           response_data = response_data + chunk
                           yield f"data: {formatted_chunk}\n\n"
                           await asyncio.sleep(0.01)
                        
                        formatted_chunk = json.dumps({"done" : True })
                        yield f"data: {formatted_chunk}\n\n"
                        

                        
                        markdown_response = markdown  .markdown(response_data)
                        last_question_obj.response = markdown_response
                        await sync_to_async(last_question_obj.save)()
                    except Exception as e:
                        print(f"Error during retrieval or LLM response: {e}")
                else:
                    yield "data: No previous questions found\n\n"
            except Exception as e:
                yield f"data: Error occurred: {str(e)}\n\n"

        # Streaming response for Server-Sent Events (SSE)
        response = StreamingHttpResponse(event_stream(), content_type='text/event-stream')
        response['Cache-Control'] = 'no-cache'
        return response

    # else:
    #     # Handle unsupported HTTP methods
    #     return JsonResponse({"error": "Invalid request method"}, status=405)

    return HttpResponse('Working')

def chat(request):
    user_coversation = QuestionHistory.objects.filter(user=request.user)
    context = {
        'user_coversation' : user_coversation
        }
    return render(request , 'chat.html' , context)