from django.shortcuts import render, HttpResponse
from django.http import JsonResponse , StreamingHttpResponse
from rest_framework import status
from .ollama_doc_init import  retriever, format_docs,  llm, chain
from django.views.decorators.csrf import csrf_exempt
from asgiref.sync import sync_to_async
import asyncio
from .models import QuestionHistory, ChatInstance
import json
from langchain_core.messages import AIMessage, HumanMessage , SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough
async def ask_questions(request, id):
    
    """
    Handles both POST (question submission) and GET (server-sent events) methods.
    """

    try:
        instance = await sync_to_async(ChatInstance.objects.get)(id=id)
        await sync_to_async(instance.save)()
    except ChatInstance.DoesNotExist:
        return HttpResponse('Page not found!')
    

    async def get_full_history():
        """
        Fetch all previous messages to build the conversation context.
        """
        # Fetch history asynchronously
        history = await sync_to_async(list)(
            QuestionHistory.objects.filter(instance=instance, response__isnull = False)
        )
       
        # Build conversation history
        conversation_list = []
        for record in history:
            conversation_list.append(HumanMessage(content=record.question))
            conversation_list.append(AIMessage(content=record.response))
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
                    response_data = ""


                    context_docs = await sync_to_async(retriever.get_relevant_documents)(query)
                    formatted_context = format_docs(context_docs)

            

                    # Get full conversation history and append the current query
                    message_history = await get_full_history()
                    message_history.append(HumanMessage(content=query))

                    # Prepare the input for the language model
                    chain_input = {
                        "context": formatted_context,
                        "messages": message_history,
                        }
                    
                    prompt = ChatPromptTemplate.from_messages(
                    [
                        SystemMessage(
                            content=f'''
                            You are a highly knowledgeable and professional economics expert specializing in Ethiopia's economic data. 
                            Your name is **MoPD Chat Bot**. Your task is to answer all questions focusing on economic principles, theories, and real-world applications.
                
                            - If a question is unrelated to economics, answer it without incorporating economic concepts.
                            - If a country is not explicitly mentioned, assume the question pertains to Ethiopia.
                            - Do not include formula details in your responses.
                            - Use **only verified document data** as the primary source for your responses.
                            - Clearly indicate whether the information is **verified** (from the document) or **not verified** (external or uncertain).
                            - If no relevant information is found in the provided documents, state: "Can't find relevant information in the provided document."
                            - **Do not generate or add any data that is not explicitly provided in the document**, even if it is seemingly trivial or inferred (e.g., values like "3" or assumptions based on general knowledge).
                            - If a user greets you (e.g., "hi," "hello," or any similar greeting), respond by introducing yourself, stating that your name is **MoPD Chat Bot**, and listing the available documents loaded into the system.
                
                            **Ethiopian Calendar Conversion**:
                            - Ethiopian calendar years (EFY, EC) can be approximated to Gregorian years by adding 7 years.
                
                            Ensure all responses are returned in **HTML format** with the following structure:
                            - Use `<h3>` for headings.
                            - Use `<p>` for body text.
                            - Use `<ul>` and `<li>` for listing items.
                            - For table-based responses:
                              - Wrap the `<table>` element inside a `<div class="table-responsive">` container.
                              - Use `<table class="table">` for styling.
                              - Include a `<thead>` section for the table header.
                              - Close the `</div>` tag at the end to maintain proper layout.
                
                            **Note**: Only documents loaded into the system are considered verified sources.
                
                            ## Context:
                            {formatted_context}
                
                            ## Question:
                            {query}
                
                            ## Response:
                            Please provide your response using the structure outlined above, ensuring adherence to the specified HTML format. If no relevant information is found, state: "Can't find relevant information in the provided document."
                            '''
                        ),
                        MessagesPlaceholder(variable_name="messages"),
                    ])



                  
                    try:
                        for chunk in (prompt | llm).stream(chain_input):  # Pass query as a str
                           formatted_chunk = json.dumps({"chunk" : chunk.content })
                           response_data = response_data + chunk.content
                           yield f"data: {formatted_chunk}\n\n"
                           await asyncio.sleep(0.01)
                        
                        formatted_chunk = json.dumps({"done" : True })
                        yield f"data: {formatted_chunk}\n\n"
                        
                        
                        last_question_obj.response = response_data
                        await sync_to_async(last_question_obj.save)()
                    except Exception as e:
                        print("error on llm response", e)

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