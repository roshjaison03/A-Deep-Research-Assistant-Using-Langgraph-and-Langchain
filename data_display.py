def display_research_improved(result):
    """Display research output with better formatting and data extraction"""
    
    print("\n" + "="*100)
    print("🎯 ADVANCED RESEARCH REPORT")
    print("="*100)
    
 
    topic_info = {}
    if isinstance(result.get('topic'), dict):
        topic_info = result['topic']
    elif hasattr(result.get('topic'), 'dict'):  
        topic_info = result['topic'].dict()
    elif hasattr(result.get('topic'), 'model_dump'): 
        topic_info = result['topic'].model_dump()
    

    print(f"\n📋 RESEARCH OVERVIEW")
    print(f"   {'─'*40}")
    if topic_info:
        print(f"   🔹 Topic: {topic_info.get('title', 'N/A')}")
        print(f"   🔹 Domain: {topic_info.get('domain', 'N/A')}")
        print(f"   🔹 Complexity: {topic_info.get('complexity', 'N/A')}")
        if topic_info.get('subtopics'):
            print(f"   🔹 Subtopics: {', '.join(topic_info['subtopics'])}")
    else:
        print(f"   Topic data not found in result")
    
    print(f"   🔹 Research Phase: {result.get('research_phase', 'N/A')}")
    print(f"   🔹 Sources Analyzed: {len(result.get('sources', []))}")
    print(f"   🔹 Key Findings: {len(result.get('findings', []))}")

    print(f"\n📝 RESEARCH PLAN")
    print(f"   {'─'*40}")
    

    research_plan = None
    if 'metadata' in result and 'research_plan' in result['metadata']:
        research_plan = result['metadata']['research_plan']
    elif 'analysis' in result and 'comprehensive_analysis' in result['analysis']:
        research_plan = result['analysis']['comprehensive_analysis']
    
    if research_plan:
    
        lines = research_plan.split('\n')[:10]
        for line in lines:
            if line.strip():
                print(f"   {line}")
        if len(research_plan.split('\n')) > 10:
            print(f"   ... (truncated, full plan: {len(research_plan.split())} words)")
    else:
        print("   No detailed research plan found")
    

    sources = result.get('sources', [])
    print(f"\n📚 SOURCES FOUND ({len(sources)})")
    print(f"   {'─'*40}")
    
    for i, source in enumerate(sources, 1):
   
        title = source.get('title', 'Untitled')
        if title == 'Untitled' and 'content' in source:
      
            content = source.get('content', '')
            if content and len(content.split()) > 2:
                title = ' '.join(content.split()[:5]) + '...'
        
        source_type = source.get('source', 'unknown').upper()
        relevance = source.get('relevance_score', 0)
        
        print(f"   {i}. [{source_type}] {title}")
        
       
        if 'content' in source and source['content']:
            content = source['content']
            snippet = content[:150].replace('\n', ' ')
            if len(content) > 150:
                snippet += '...'
            print(f"      └─ {snippet}")
        

        meta_info = []
        if 'published' in source:
            meta_info.append(f"Published: {source['published']}")
        if 'authors' in source and source['authors']:
            authors = source['authors'][:2]
            meta_info.append(f"Authors: {', '.join(authors)}" + 
                           (f" + {len(source['authors'])-2} more" if len(source['authors']) > 2 else ""))
        if relevance:
            meta_info.append(f"Relevance: {relevance:.2f}")
        
        if meta_info:
            print(f"      └─ {' | '.join(meta_info)}")

    findings = result.get('findings', [])
    print(f"\n🔍 KEY FINDINGS ({len(findings)})")
    print(f"   {'─'*40}")
    
    for i, finding in enumerate(findings, 1):
        content = finding.get('content', '').strip()
        category = finding.get('category', 'observation').upper()
        confidence = finding.get('confidence', 0)

        if content.startswith('#') or content.startswith('##'):
            content = content.lstrip('#').strip()
        
        print(f"   {i}. [{category}]")
        print(f"      {content}")
        
        if confidence:
            confidence_bar = '█' * int(confidence * 10) + '░' * (10 - int(confidence * 10))
            print(f"      Confidence: {confidence:.2f} [{confidence_bar}]")
        print()
    

    if 'analysis' in result:
        analysis = result['analysis']
        print(f"\n🧠 ANALYSIS INSIGHTS")
        print(f"   {'─'*40}")
        
        if 'comprehensive_analysis' in analysis:
            insights = analysis['comprehensive_analysis']

            lines = insights.split('\n')
            for line in lines[:8]:  
                if line.strip() and len(line.strip()) > 20:
                    print(f"   • {line.strip()}")
        
        if 'confidence_score' in analysis:
            print(f"   🔹 Overall Confidence Score: {analysis['confidence_score']:.2f}/1.0")

    limitations = result.get('limitations', [])
    if limitations:
        print(f"\n⚠️ IDENTIFIED LIMITATIONS")
        print(f"   {'─'*40}")
        for i, limitation in enumerate(limitations, 1):
            print(f"   {i}. {limitation}")
    
    recommendations = result.get('recommendations', [])
    if recommendations:
        print(f"\n💡 RESEARCH RECOMMENDATIONS")
        print(f"   {'─'*40}")
        for i, recommendation in enumerate(recommendations, 1):
            print(f"   {i}. {recommendation}")

    if 'final_paper' in result:
        paper = result['final_paper']
        print(f"\n📄 FINAL RESEARCH PAPER")
        print(f"   {'─'*40}")
        print(f"   Title: {paper.get('title', 'Research Report')}")
        print(f"   Status: ✓ COMPLETED")
        print(f"   Word Count: {paper.get('word_count', 0):,}")
        print(f"   Citations: {paper.get('citations_count', 0)}")
        

        if 'sections' in paper:
            print(f"   Sections: {len(paper['sections'])}")
            print(f"   {'─'*40}")
            for section in paper['sections'][:5]: 
                print(f"   • {section}")
            if len(paper['sections']) > 5:
                print(f"   • ... and {len(paper['sections']) - 5} more")
        
    
        if 'content' in paper and 'abstract' in paper['content']:
            abstract = paper['content']['abstract']
            print(f"\n   ABSTRACT PREVIEW:")
            print(f"   {'─'*40}")
            lines = abstract.split('\n')[:4]
            for line in lines:
                if line.strip():
                    print(f"   {line}")
            if len(abstract) > 500:
                print(f"   ... (full abstract: {len(abstract)} characters)")
    
    # 8. EXECUTIVE SUMMARY
    print(f"\n⭐ EXECUTIVE SUMMARY")
    print(f"   {'─'*40}")
    

    summary_parts = []
    if topic_info:
        summary_parts.append(f"Research on '{topic_info.get('title', 'the topic')}'")
    summary_parts.append(f"analyzed {len(sources)} sources")
    summary_parts.append(f"identified {len(findings)} key findings")
    
    if limitations:
        summary_parts.append(f"noted {len(limitations)} limitations")
    
    if recommendations:
        summary_parts.append(f"proposed {len(recommendations)} recommendations")
    
    print(f"   This research {' and '.join(summary_parts)}.")
    
    if 'analysis' in result and 'confidence_score' in result['analysis']:
        conf = result['analysis']['confidence_score']
        confidence_level = "High" if conf > 0.7 else "Moderate" if conf > 0.5 else "Preliminary"
        print(f"   Overall confidence: {confidence_level} ({conf:.2f}/1.0)")
    
    print(f"\n" + "="*100)
    print("✅ RESEARCH COMPLETE")
    print("="*100)