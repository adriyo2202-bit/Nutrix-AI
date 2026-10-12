import urllib.request
import urllib.parse
import json
import logging
import ssl

logger = logging.getLogger(__name__)

class OpenFoodFactsRetriever:
    """
    Retrieves product information from the Open Food Facts API.
    """
    def __init__(self):
        self.base_url = "https://world.openfoodfacts.org/cgi/search.pl"

    def retrieve(self, query):
        """
        Extracts product name from query and searches Open Food Facts API.
        """
        # A simple heuristic to extract potential product names from the query.
        # In a more advanced system, an LLM entity extractor would be used.
        # Here we just pass the full query (or heavily filtered query) to the OFF search API.
        # Clean the query of stop words
        stop_words = ["is", "what", "are", "the", "ingredients", "in", "healthy", "bad", "for", "me", "tell", "about", "a", "an", "does", "have"]
        words = query.lower().split()
        search_terms = [w for w in words if w not in stop_words]
        
        if not search_terms:
            search_terms = words # fallback to full query
            
        search_str = " ".join(search_terms)
        
        encoded_query = urllib.parse.quote(search_str)
        url = f"{self.base_url}?search_terms={encoded_query}&search_simple=1&action=process&json=1"
        
        try:
            context = ssl._create_unverified_context()
            req = urllib.request.Request(url, headers={'User-Agent': 'NutrixAI/1.0'})
            
            # Short 2-second timeout so it never hangs local pipeline
            with urllib.request.urlopen(req, context=context, timeout=2) as response:
                res_data = json.loads(response.read().decode('utf-8'))
                
                products = res_data.get('products', [])
                if not products:
                    return {"results": []}
                    
                # Take the top matched product
                p = products[0]
                
                result = {
                    "product_name": p.get("product_name", "Unknown Product"),
                    "brands": p.get("brands", "Unknown Brand"),
                    "nutriscore_grade": p.get("nutriscore_grade", "Unknown"),
                    "nova_group": p.get("nova_group", "Unknown"),
                    "ingredients_text": p.get("ingredients_text", "Not provided"),
                    "nutrient_levels": p.get("nutrient_levels", {}),
                    "url": p.get("url", "https://world.openfoodfacts.org")
                }
                
                # Format into a nice context chunk
                content = (
                    f"Product Name: {result['product_name']} (Brand: {result['brands']})\n"
                    f"Nutri-Score: {str(result['nutriscore_grade']).upper()}\n"
                    f"NOVA Processing Group: {result['nova_group']} (1=Unprocessed, 4=Ultra-processed)\n"
                    f"Ingredients: {result['ingredients_text']}\n"
                    f"Nutrient Levels (Low/Mod/High): {json.dumps(result['nutrient_levels'])}\n"
                )
                
                return {
                    "results": [{
                        "title": f"Open Food Facts: {result['product_name']}",
                        "content": content,
                        "url": result['url']
                    }]
                }
        except Exception as e:
            logger.error(f"Open Food Facts API Error: {e}")
            return {"results": []}
