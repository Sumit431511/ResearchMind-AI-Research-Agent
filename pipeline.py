from agents import build_reader_agent, build_search_agent, writer_chain, crictic_chain

def run_research_pipeline(topic:str)->dict:
    state = {}

    print("\n"+"="*50)
    print("Step 1 - search agent is working...")
    print("="*50)

    search_agent = build_search_agent()
    search_result = search_agent.invoke({
        "messages":[("user",f"Find recent, reliable and detailed information about : {topic}")]
    })

    state["search_result"] = search_result['messages'][-1].content

    print("\n search result",state["search_result"])

    print("\n"+"="*50)
    print("Step 2 - reader agent is working...")
    print("="*50)
    print(type(state['search_result']))
    reader_agent = build_reader_agent()
    reader_result = reader_agent.invoke({
        "messages":[("user",
                   f"Based om the following search results about '{topic}',"
                   f"pick the most relevant URL and scrape it for deeper content.\n\n"
                   f"Search Results:\n{state['search_result'][:800]}"
                   )]
    })
    state["scarped_content"] = reader_result['messages'][-1].content

    print("\nScarped Content : \n",state["scarped_content"])

    print("\n"+"="*50)
    print("Step 3 - final report is generating...")
    print("="*50)

    research_combined = (
        f"SEARCH RESULT : \n{state['search_result']}\n\n"
        f"DETAILED SCARPED CONTENT : \n {state['scarped_content']}"
    )

    state["report"] = writer_chain.invoke({
        "topic":topic,
        "research":research_combined
    })

    print("\n Final Report\n",state['report'])

    print("\n"+"="*50)
    print("Step 4 - Crictic is reviewing the report...")
    print("="*50)

    state["feedback"] = crictic_chain.invoke({
        "report":state['report']
    })

    print("\nCrictic report\n",state['feedback'])

    return state


if __name__ == "__main__":
    topic = input("\nEnter a research topic : ")
    run_research_pipeline(topic)