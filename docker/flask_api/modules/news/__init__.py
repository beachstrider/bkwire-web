from .base import NewsScraper
from .apparel_news import ApparelNewsScraper
from .chemical_news import ChemicalNewsScraper
from .business_services_news import BusinessServicesNewsScraper
from .construction_news import ConstructionNewsScraper
from .financial_services_news import FinancialServicesNewsScraper
from .food_news import FoodNewsScraper
from .furniture_news import FurnitureNewsScraper
from .hospitality_news import HospitalityNewsScraper
from .medical_news import MedicalNewsScraper
from .manufacturing_news import ManufacturingNewsScraper
from .metals_news import MetalsNewsScraper
from .energy_news import OilAndGasNewsScraper
from .paper_and_packaging_news import PaperAndPackagingNewsScraper
from .real_estate_news import RealEstateNewsScraper
from .transportation_news import TransportationNewsScraper
from .retail_news import RetailNewsScraper
from .technology_news import TechnologyNewsScraper
from .general_news import GeneralNewsScraper

INDUSTRY_SCRAPER_MAPPING = {
    "general": GeneralNewsScraper,
    "apparel": ApparelNewsScraper,
    "business services": BusinessServicesNewsScraper,
    "chemical": ChemicalNewsScraper,
    "construction": ConstructionNewsScraper,
    "financial services": FinancialServicesNewsScraper,
    "food": FoodNewsScraper,
    "furniture": FurnitureNewsScraper,
    "hospitality": HospitalityNewsScraper,
    "medical": MedicalNewsScraper,
    "manufacturing": ManufacturingNewsScraper,
    "metals": MetalsNewsScraper,
    "energy": OilAndGasNewsScraper,
    "paper and packaging": PaperAndPackagingNewsScraper,
    "real estate": RealEstateNewsScraper,
    "transportation": TransportationNewsScraper,
    "retail": RetailNewsScraper,
    "technology": TechnologyNewsScraper,
}
