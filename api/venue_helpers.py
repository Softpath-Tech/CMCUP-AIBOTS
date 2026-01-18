
# Validates assembly name against district list or returns None
def search_assembly_incharge_helper(query_name):
    # Since we lack specific assembly data, we map to District Officer.
    # We try to match query_name to a known District.
    # If match, return District Officer details.
    # If NOT match, we say "Details not found".
    
    from rag.location_search import search_district_officer
    
    # Try searching as District first
    res = search_district_officer(query_name)
    if res:
        # It's a district HQ assembly
        return {
            "assembly_name": res['district_name'],
            "incharge_name": "See District Officer",
            "mobile_no": res['contact_no'],
            "district_name": res['district_name'],
            "type": "District HQ Assembly"
        }
        
    # If not a district match, we can't find it.
    # Return placeholder
    return None

def format_venue_response(level, data, session_id=None):
    """
    Format the VENUE response as per user requirement.
    
    Gram Panchayat / Cluster Level: [Name]
    Venue: [Venue]
    In-charge Details: ...
    Mandal Officer Details: ...
    """
    # from rag.translations import get_msg # Unused and causes import error
    
    txt = ""
    # We might need to fetch parent details if not present in data
    
    if level == "Cluster":
        c_name = data.get('clustername', 'N/A')
        venue = data.get('clustername', 'N/A') # Assuming Venue = Cluster Name for now
        c_inc = data.get('incharge_name', 'N/A')
        c_mob = data.get('mobile_no', 'N/A')
        
        m_name = data.get('mandal_name', 'N/A')
        # Fetch Mandal Officer
        from rag.location_search import search_mandal_incharge
        m_res = search_mandal_incharge(m_name) if m_name != 'N/A' else None
        m_inc = m_res.get('incharge_name', 'N/A') if m_res else "N/A"
        m_mob = m_res.get('mobile_no', 'N/A') if m_res else "N/A"
        
        txt = f"**Gram Panchayat / Cluster Level:** {c_name}\n"
        txt += f"**Venue:** {venue}\n\n"
        txt += f"**In-charge Details:**\nName: {c_inc}\nMobile: {c_mob}\n\n"
        txt += f"**Mandal Officer Details:**\nName: {m_inc}\nMobile: {m_mob}"
        
    elif level == "Mandal":
        m_name = data.get('mandal_name', 'N/A')
        venue = m_name # Venue = Mandal HQ
        m_inc = data.get('incharge_name', 'N/A')
        m_mob = data.get('mobile_no', 'N/A')
        
        # Assembly Details (Placeholder)
        # We don't have mapping from Mandal -> Assembly efficiently without DB.
        # Check if user wanted Assembly Incharge.
        # "Mandal and Assembly Incharge Details"
        
        txt = f"**Mandal Level:** {m_name}\n"
        txt += f"**Venue:** {venue} (Mandal HQ)\n\n"
        txt += f"**In-charge Details:**\nName: {m_inc}\nMobile: {m_mob}\n\n"
        txt += f"**Assembly In-charge:**\n(Contact District Incharge)"

    elif level == "Assembly":
        a_name = data.get('assembly_name', 'N/A')
        venue = a_name
        # Assembly Incharge (Mapped to District Incharge or N/A)
        # Details found via search_assembly_incharge_helper which returns district info if matched
        
        inc_name = data.get('incharge_name', 'N/A')
        inc_mob = data.get('mobile_no', 'N/A')
        
        d_name = data.get('district_name', 'N/A')
        # Fetch District Officer
        from rag.location_search import search_district_officer
        d_res = search_district_officer(d_name) if d_name != 'N/A' else None
        d_inc = d_res.get('special_officer_name', 'N/A') if d_res else "N/A"
        d_mob = d_res.get('contact_no', 'N/A') if d_res else "N/A"
        
        txt = f"**Assembly Constituency Level:** {a_name}\n"
        txt += f"**Venue:** {venue} (Constituency HQ)\n\n"
        txt += f"**In-charge Details:**\nName: {inc_name}\nMobile: {inc_mob}\n\n"
        txt += f"**District In-charge Details:**\nName: {d_inc}\nMobile: {d_mob}"

    elif level == "District":
        d_name = data.get('district_name', 'N/A')
        inc_name = data.get('special_officer_name', 'N/A')
        inc_mob = data.get('contact_no', 'N/A')
        
        txt = f"**District Level:** {d_name}\n"
        txt += f"**Venue:** {d_name} (District HQ)\n\n"
        txt += f"**District In-charge Details:**\nName: {inc_name}\nMobile: {inc_mob}"
        
    return txt
