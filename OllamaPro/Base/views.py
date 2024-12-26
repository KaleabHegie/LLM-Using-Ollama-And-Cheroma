from django.shortcuts import render, HttpResponse
from django.http import JsonResponse , StreamingHttpResponse
from rest_framework import status
from .ollama_doc_init import chain, retriever
from django.views.decorators.csrf import csrf_exempt
from asgiref.sync import sync_to_async
import asyncio
from .models import QuestionHistory, ChatInstance
import json
from langchain_core.messages import SystemMessage


async def ask_questions(request, id):
    
    """
    Handles both POST (question submission) and GET (server-sent events) methods.
    """

    try:
        instance = await sync_to_async(ChatInstance.objects.get)(id=id)
    except ChatInstance.DoesNotExist:
        return HttpResponse('Page not found!')
    

    def format_docs_new(docs):
        return "\n\n".join(f"{doc['role']}: {doc['content']}" for doc in docs if doc.get('content') != 'None')


    async def get_full_history():
        """
        Fetch all previous messages to build the conversation context.
        """
        # Fetch history asynchronously
        history = await sync_to_async(list)(
            QuestionHistory.objects.filter(instance=instance, response__isnull = False).order_by("created_at")
        )

       

        
        # Build conversation history
        conversation_list = []
        for record in history:
            conversation_list.append({"role": "user", "content": record.question})
            conversation_list.append({"role": "assistant", "content": record.response})
        

        return conversation_list
    
    

    if request.method == 'POST':
        
        question = request.POST.get('question', '').strip()
        try:
              
             # Convert to sync to perform ORM operations
              created_obj = await sync_to_async(QuestionHistory.objects.create)(
                question=question,
                instance = instance,
             )
              
              created_obj_id = created_obj.id
              
              if(not instance.title):
                msg = await sync_to_async(QuestionHistory.objects.filter(instance = instance).first)()
                instance.title = msg.question
                await sync_to_async(instance.save)()

              none_instances = await sync_to_async(ChatInstance.objects.filter)(title=None)
              await sync_to_async(none_instances.delete)()

              
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
                last_question_obj = await sync_to_async(QuestionHistory.objects.filter(instance = instance).last)()
                if last_question_obj:
                    query = last_question_obj.question
                    
                    conversation_history = await get_full_history()
                    conversation_history.append({"role": "user", "content": query})
                    llm_history = format_docs_new(conversation_history) or query
                    # Ensure you're passing the correct input to the chain
                    response_data = ""
                    
                    print("printing...", llm_history)
                  
                    
                    for chunk in chain.stream(llm_history):  # Pass query as a string
                       formatted_chunk = json.dumps({"chunk" : chunk })
                       response_data = response_data + chunk
                       yield f"data: {formatted_chunk}\n\n"
                       await asyncio.sleep(0.01)
                    
                    formatted_chunk = json.dumps({"done" : True })
                    yield f"data: {formatted_chunk}\n\n"
                    
                    
                    last_question_obj.response = response_data
                    await sync_to_async(last_question_obj.save)()

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

def chat(request, id=None):
    chat_instances = ChatInstance.objects.filter(user=request.user)
    is_new = False
    try:
        if(id == 0):
            instance = ChatInstance()
            instance.user = request.user
            instance.save()
            is_new = True
        else:
            instance = ChatInstance.objects.get(id=id)
        histories = QuestionHistory.objects.filter(instance = instance)
    except ChatInstance.DoesNotExist:
        return HttpResponse('Page not found!')
    context = {
        'chat_instances' : chat_instances,
        'instance' : instance,
        'user_coversation' : histories,
        'is_new' : is_new
        
        }
    return render(request , 'chat.html' , context)