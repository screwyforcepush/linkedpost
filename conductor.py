    from common_util.memory import set_entity_memory_long_cache, warm_cache, get_entities
    from queryDB import tools, set_seed_query, get_seed_query, get_latest_ai_research
    from langchain_experimental.plan_and_execute import PlanAndExecute, load_agent_executor, load_chat_planner
    import langchain
    from datetime import datetime

    langchain.debug = True

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    set_seed_query("Find an interesting and unique connection between different Generative AI research findings and techniques. Include all information that would aid in the application of the connected techniques to Video Streaming Analytics. " + timestamp)
    set_entity_memory_long_cache([])
    latest_research = get_latest_ai_research()
    entities = get_entities()
entities = get_entities()
