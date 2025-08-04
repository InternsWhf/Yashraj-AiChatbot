# Western Heat & Forge Company Data
# Extracted from https://www.westernheatforge.com/

COMPANY_DATA = {
    "company_name": "Western Heat & Forge",
    "website": "https://www.westernheatforge.com/",
    "email": "SALES@WesternHeatForge.com",
    "phone": "+91 20 6635 9200",
    "address": "J-2 'S' Block, MIDC, Telco Road Bhosari, Pune - 411026, INDIA",
    
    "about": {
        "founded": "1982",
        "employees": "> 500 employees",
        "exports": "> 25% Exports",
        "description": "Global Supplier of Machined, Turnkey and Tested Components",
        "achievements": [
            "1st Company in India to provide forged, machined, coated, cladded components",
            "WHF is the ONLY Company in India which is both API 20B and API 20C certified",
            "Fully Integrated Open and Closed Die Forging Facility with annual capacity of 25,000 Tons",
            "Closed Die Forging – 18,000 Tons. Single piece < 100 kgs",
            "Open Die Forging – 7,000 Tons. Single piece < 4000 kgs",
            "ISO 9001 approved Machining Components Division with Coating and Cladding facilities – over 60% machined parts"
        ]
    },
    
    "services": {
        "forging": {
            "name": "Forging",
            "description": "Forging, Heat Treatment, Machining, Testing (Hydrostatic and other)",
            "capacity": "25,000 Tons annually",
            "types": ["Closed Die Forging", "Open Die Forging"]
        },
        "heat_treatment": {
            "name": "Heat Treatment",
            "description": "Expert in Heat Treatment with NABL accredited facilities",
            "materials": ["Carbon steel", "Carburizing steels", "Low alloy steel", "High alloy steel", "Stainless steel"],
            "equipment": ["Batch furnace with auto charger", "Continuous furnace with extractor mechanism", "Deep Throat Hardness Tester"]
        },
        "machining": {
            "name": "Machining",
            "description": "ISO 9001 approved Machining Components Division",
            "capacity": "Over 60% machined parts"
        },
        "coating": {
            "name": "Coating",
            "description": "Joint Venture with Technicoat to set up a state of the art Coating facility in India"
        },
        "cladding": {
            "name": "Cladding",
            "description": "Inconel and other overlays. Approved by a global Oil and Gas OE"
        },
        "lab_testing": {
            "name": "Lab Testing",
            "description": "Metallurgical and Metrological Lab Testing Services",
            "types": ["Metallurgical Lab", "Metro-logical Lab"]
        }
    },
    
    "products": {
        "categories": [
            "Valves",
            "Fittings", 
            "Flanges",
            "Couplings",
            "Drill Bits",
            "Machined Components",
            "Coated Components",
            "Cladded Components"
        ],
        "specialty": "Supermarket of over 250 Machined Components"
    },
    
    "industries": [
        "Oil & Gas",
        "Power",
        "Mining",
        "Construction & Infrastructure", 
        "Automobile",
        "Defence"
    ],
    
    "certifications": [
        "API 20B Certified",
        "API 20C Certified",
        "ISO 9001",
        "NABL Accredited"
    ],
    
    "customers": {
        "testimonials": [
            {
                "quote": "WHF helped us reduce leadtimes and costs by taking over our supply chain management for machined components by creating a supermarket for over 250 of our core components. They did this while maintaining the highest supplier ratings in terms of quality and on-time delivery.",
                "author": "R Roshan",
                "company": "Global Construction Equipment OEM"
            },
            {
                "quote": "I used to have to connect with four different vendors to get forgings, machining, cladding and hydrostatic testing done for our valve bodies. Now I go to WHF who has simplified our purchasing process by taking full responsibility for delivering turnkey tested components from start to finish.",
                "author": "Anonymous",
                "company": "Global Oil & Gas and Valves Manufacturer"
            },
            {
                "quote": "WHF has made significant investments to add more value to the components that they supply us by adding finished machining, coating, cladding and testing capabilities.",
                "author": "Anonymous", 
                "company": "Major Oil & Gas OEM"
            }
        ]
    },
    
    "solutions": [
        "Hydrostatic Testing of components compliant to International and IBR certification",
        "INCONEL CLAD FULLY MACHINED COMPONENTS FOR OIL & GAS"
    ]
}

def get_company_info():
    """Get formatted company information"""
    return COMPANY_DATA

def search_company_data(query):
    """Search through company data for relevant information"""
    query_lower = query.lower()
    results = []
    
    # Search in company basic info
    if any(word in query_lower for word in ["contact", "email", "phone", "address"]):
        results.append(f"**Contact Information:**\n📧 Email: {COMPANY_DATA['email']}\n📞 Phone: {COMPANY_DATA['phone']}\n📍 Address: {COMPANY_DATA['address']}")
    
    # Search in about section
    if any(word in query_lower for word in ["about", "founded", "history", "company", "who"]):
        about = COMPANY_DATA['about']
        results.append(f"**About Western Heat & Forge:**\n🏢 Founded: {about['founded']}\n👥 Employees: {about['employees']}\n🌍 Exports: {about['exports']}\n📋 {about['description']}")
    
    # Search in services
    if any(word in query_lower for word in ["service", "forging", "heat treatment", "machining", "coating", "cladding", "testing"]):
        services = COMPANY_DATA['services']
        service_list = []
        for service_name, service_info in services.items():
            service_list.append(f"🔧 **{service_info['name']}**: {service_info['description']}")
        results.append("**Our Services:**\n" + "\n".join(service_list))
    
    # Search in products
    if any(word in query_lower for word in ["product", "valve", "fitting", "flange", "component"]):
        products = COMPANY_DATA['products']
        results.append(f"**Our Products:**\n📦 Categories: {', '.join(products['categories'])}\n🏪 Specialty: {products['specialty']}")
    
    # Search in industries
    if any(word in query_lower for word in ["industry", "sector", "market"]):
        industries = COMPANY_DATA['industries']
        results.append(f"**Industries We Serve:**\n🏭 {', '.join(industries)}")
    
    # Search in certifications
    if any(word in query_lower for word in ["certification", "certified", "api", "iso", "nabl"]):
        certs = COMPANY_DATA['certifications']
        results.append(f"**Certifications:**\n🏆 {', '.join(certs)}")
    
    # Search in customers/testimonials
    if any(word in query_lower for word in ["customer", "testimonial", "client", "feedback"]):
        testimonials = COMPANY_DATA['customers']['testimonials']
        testimonial_text = "**Customer Testimonials:**\n"
        for i, testimonial in enumerate(testimonials[:2], 1):  # Show first 2
            testimonial_text += f"\n💬 **{testimonial['company']}**: \"{testimonial['quote'][:150]}...\""
        results.append(testimonial_text)
    
    return results

class CompanyDataManager:
    def __init__(self):
        pass
    
    def get_company_info(self):
        """Get formatted company information"""
        return get_company_info()
    
    def search_company_data(self, query):
        """Search through company data for relevant information"""
        return search_company_data(query) 