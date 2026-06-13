import shodan

# Your Shodan API key
API_KEY = 'ENTER_API_KEY'

# Initialize the Shodan API client
api = shodan.Shodan(API_KEY)

try:
    # Basic search - returns first page only
    results = api.search('org:"LC"')
    
    # Optional: Add time-based filtering
    # results = api.search('org:"LC" before:07/06/2026 after:01/06/2026')
    
    print(f"Found {results['total']} results for LC\n")
    
    # Display results
    for result in results['matches']:
        print(f"IP: {result['ip_str']}")
        print(f"Port: {result['port']}")
        print(f"Service: {result.get('_shodan', {}).get('module', 'Unknown')}")
        print(f"Last Update: {result.get('timestamp', 'N/A')}")
        if result.get('data'):
            print(f"Banner: {result['data'][:100]}...")
        print("-" * 50)
    
    # PAGINATION: Uncomment the section below to iterate through all results
    # Useful for large result sets
    # 
    # page = 1
    # while True:
    #     results = api.search('org:"LC"', page=page)
    #     
    #     if not results['matches']:
    #         break
    #         
    #     for result in results['matches']:
    #         print(f"IP: {result['ip_str']}")
    #         print(f"Port: {result['port']}")
    #         print(f"Service: {result.get('_shodan', {}).get('module', 'Unknown')}")
    #         print(f"Last Update: {result.get('timestamp', 'N/A')}")
    #         if result.get('data'):
    #             print(f"Banner: {result['data'][:100]}...")
    #         print("-" * 50)
    #     
    #     page += 1
        
except shodan.APIError as e:
    print(f"Error: {e}")
