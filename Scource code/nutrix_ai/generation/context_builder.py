class ContextBuilder:
    """
    Builds the final prompt context by combining RAG chunks, Web chunks, User Context, and Chat History.
    """
    def build(self, query, user_context_dict, rag_results, web_results, off_results=None, chat_history=None):
        context_blocks = []
        if chat_history is None:
            chat_history = []
        
        if user_context_dict:
            u_str = "[PRIVATE USER CONTEXT]\n"
            if 'nutrition' in user_context_dict:
                nut = user_context_dict['nutrition']
                u_str += f"Goal: {nut['goal']} ({nut.get('diet_type', 'General')} Diet)\n"
                u_str += f"Bio: Age {nut.get('age')}, Weight {nut.get('weight_kg')}kg, Height {nut.get('height_cm')}cm\n"
            if 'active_diet_plan' in user_context_dict:
                import json
                u_str += f"**CURRENT ACTIVE DIET PLAN**: {json.dumps(user_context_dict['active_diet_plan'], indent=2)}\n"
            if 'recent_scans' in user_context_dict:
                import json
                u_str += f"**RECENTLY SCANNED LABELS**: {json.dumps(user_context_dict['recent_scans'], indent=2)}\n"
            if 'fitness' in user_context_dict:
                u_str += f"Fitness: {user_context_dict['fitness']}\n"
            if 'health_lens' in user_context_dict:
                u_str += f"Health Lens Scan: {user_context_dict['health_lens']}\n"
            context_blocks.append(u_str)
            
        if rag_results:
            rag_str = "[STABLE KNOWLEDGE / RAG]\n"
            for i, r in enumerate(rag_results):
                rag_str += f"--- Document {i+1} ---\n{r['content']}\n"
            context_blocks.append(rag_str)
            
        if off_results:
            off_str = "[OPEN FOOD FACTS DATABASE]\n"
            for i, r in enumerate(off_results):
                off_str += f"--- Source: {r.get('title', 'Product')} ---\n"
                off_str += f"{r['content']}\n"
            context_blocks.append(off_str)
            
        if web_results:
            web_str = "[CURRENT WEB SEARCH RESULTS]\n"
            for i, r in enumerate(web_results):
                # Never show mock documents to the user as real sources in citations.
                # We can feed the content to the LLM but we strip the URL so the LLM can't cite a fake URL.
                is_mock = r.get('is_mock', False)
                url = "Mock Data - Do not cite URL" if is_mock else r.get('url', 'Unknown URL')
                title = r.get('title', 'Unknown')
                
                web_str += f"--- Source: {title} ({url}) ---\n"
                if r.get('published_at'):
                    web_str += f"Published: {r['published_at']}\n"
                web_str += f"{r['content']}\n"
            context_blocks.append(web_str)
            
        final_context = "\n\n".join(context_blocks)
        
        system_prompt = f"""You are Nutrix, an extremely polite, highly intelligent conversational health and nutrition assistant.
Your goal is to answer the user's question by rigorously analyzing the provided RAG dataset and context.

Important rules:
1. EXTREMELY SIMPLE LANGUAGE: You must write in a way that is incredibly easy and fun to read. Use simple, everyday words. Keep your sentences short and punchy. No long, complicated paragraphs. Write like you are talking to a friend.
2. AESTHETIC FORMATTING: Make your output look beautiful. Use bolding to highlight key points, food names, and numbers. Use bullet points and emojis to break up the text. Create clear, short sections with clean headers.
3. CHUNK-BY-CHUNK STYLE: Present your information step-by-step. Break big ideas down into small, bite-sized chunks so the reader never feels overwhelmed.
4. NUTRITION-SPECIFIC DIET CHARTS: When asked for a diet plan, you MUST create a highly detailed Diet Chart based on the dataset. Break it down by exact meal times (e.g., Morning, Breakfast, Lunch). 
5. INDIAN CULTURAL ALIGNMENT: Use authentic Indian food names (e.g., Dal, Sabzi, Roti, Paneer) and suggest traditional Indian combinations.
6. RAG DATASET INTEGRATION: Pull all your nutritional facts, macros, and food properties directly from the provided RAG context dataset. Use this data to accurately calculate calories, protein, carbs, and fats for the diet chart.

==== CONTEXT START ====
{final_context}
==== CONTEXT END ====
"""
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add recent conversation history (max 4 messages to avoid context bloat)
        for msg in chat_history[-4:]:
            messages.append(msg)
            
        messages.append({"role": "user", "content": query})
        
        return messages
