"""
Management command to seed Samko Cars database with realistic demo vehicle inventory.
Run: python manage.py seed_cars
Run: python manage.py seed_cars --clear   (to delete all demo data first)
"""
import random
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from apps.cars.models import Car, Feature
from apps.core.models import SiteSetting, SocialMedia, Testimonial


SAMPLE_VEHICLES = [
    # Toyota
    {"make": "Toyota", "model": "Camry XSE", "year": 2021, "price": 25500000, "mileage": 42000,
     "condition": "foreign_used", "transmission": "automatic", "fuel_type": "petrol",
     "body_type": "sedan", "engine": "2.5L 4-Cylinder", "exterior_color": "Pearl White",
     "interior_color": "Black Leather", "location": "Lekki, Lagos", "status": "available",
     "is_featured": True,
     "description": "Immaculate 2021 Toyota Camry XSE with full specifications. This premium Tokunbo unit features a sport-tuned suspension, power sunroof, Apple CarPlay, and heated front seats. Fully cleared with customs documentation available."},
    
    {"make": "Toyota", "model": "Highlander XLE", "year": 2020, "price": 34000000, "mileage": 55000,
     "condition": "foreign_used", "transmission": "automatic", "fuel_type": "petrol",
     "body_type": "suv", "engine": "3.5L V6", "exterior_color": "Midnight Black",
     "interior_color": "Beige Leather", "location": "Victoria Island, Lagos", "status": "available",
     "is_featured": True,
     "description": "2020 Toyota Highlander XLE in pristine condition. 8-passenger family SUV with 3-zone climate control, bird's eye view camera, blind spot monitoring, and rear cross-traffic alert. Perfect family vehicle."},
    
    {"make": "Toyota", "model": "Land Cruiser V8", "year": 2022, "price": 105000000, "mileage": 18000,
     "condition": "foreign_used", "transmission": "automatic", "fuel_type": "diesel",
     "body_type": "suv", "engine": "5.7L V8", "exterior_color": "Graphite",
     "interior_color": "Black/Brown Leather", "location": "Maitama, Abuja", "status": "available",
     "is_featured": True,
     "description": "Full-spec 2022 Toyota Land Cruiser LC300. Executive 4WD SUV with Mark Levinson premium audio, panoramic sunroof, night vision, and 10-inch infotainment. The ultimate Nigerian road vehicle."},
    
    {"make": "Toyota", "model": "Corolla Sport", "year": 2022, "price": 18500000, "mileage": 28000,
     "condition": "foreign_used", "transmission": "cvt", "fuel_type": "hybrid",
     "body_type": "sedan", "engine": "2.0L Hybrid", "exterior_color": "Supersonic Red",
     "interior_color": "Black Fabric", "location": "Ikeja, Lagos", "status": "available",
     "is_featured": False,
     "description": "2022 Toyota Corolla Sport Hybrid. Exceptional fuel economy with sporty aesthetics. Comes with Toyota Safety Sense 2.0, 8-inch touchscreen with Apple/Android CarPlay."},
    
    {"make": "Toyota", "model": "RAV4 XLE Premium", "year": 2023, "price": 45000000, "mileage": 8000,
     "condition": "foreign_used", "transmission": "automatic", "fuel_type": "hybrid",
     "body_type": "suv", "engine": "2.5L Hybrid", "exterior_color": "Lunar Rock",
     "interior_color": "SoftTex Leather", "location": "Lekki, Lagos", "status": "available",
     "is_featured": True,
     "description": "Nearly new 2023 Toyota RAV4 XLE Premium Hybrid with outstanding fuel efficiency. Features power liftgate, heated/ventilated seats, JBL audio system, and comprehensive driver assist tech."},

    # Lexus
    {"make": "Lexus", "model": "RX 350 F-Sport", "year": 2022, "price": 56000000, "mileage": 24000,
     "condition": "foreign_used", "transmission": "automatic", "fuel_type": "petrol",
     "body_type": "suv", "engine": "3.5L V6", "exterior_color": "Atomic Silver",
     "interior_color": "Black F-Sport Leather", "location": "Victoria Island, Lagos", "status": "available",
     "is_featured": True,
     "description": "2022 Lexus RX350 F-Sport with exclusive F-Sport appearance package. Mark Levinson 15-speaker audio, 12.3-inch split-screen infotainment, panoramic moonroof, and adaptive suspension. The pinnacle of luxury SUVs."},
    
    {"make": "Lexus", "model": "ES 350", "year": 2021, "price": 39000000, "mileage": 35000,
     "condition": "foreign_used", "transmission": "automatic", "fuel_type": "petrol",
     "body_type": "sedan", "engine": "3.5L V6", "exterior_color": "Caviar Black",
     "interior_color": "Flaxen Leather", "location": "Garki, Abuja", "status": "available",
     "is_featured": False,
     "description": "2021 Lexus ES350 Ultra Luxury edition. 12.3-inch touchscreen, 17-speaker Mark Levinson audio, heated/ventilated front seats, and panoramic moonroof. Supremely quiet and refined cabin."},
    
    {"make": "Lexus", "model": "GX 460 Premium", "year": 2020, "price": 62000000, "mileage": 48000,
     "condition": "foreign_used", "transmission": "automatic", "fuel_type": "petrol",
     "body_type": "suv", "engine": "4.6L V8", "exterior_color": "Starfire Pearl",
     "interior_color": "Sepia Leather", "location": "Lekki, Lagos", "status": "reserved",
     "is_featured": False,
     "description": "2020 Lexus GX460 Premium with KDSS electronic suspension. 3-row seating, multi-terrain select, center locking differential, and Lexus Safety System. Exceptional off-road capability with executive comfort."},

    # Mercedes-Benz
    {"make": "Mercedes-Benz", "model": "GLE 450 AMG-Line", "year": 2021, "price": 85000000, "mileage": 22000,
     "condition": "foreign_used", "transmission": "automatic", "fuel_type": "petrol",
     "body_type": "suv", "engine": "3.0L Turbo I6 MHEV", "exterior_color": "Designo Selenite Grey",
     "interior_color": "Nappa Leather Macchiato Beige", "location": "Ikoyi, Lagos", "status": "available",
     "is_featured": True,
     "description": "2021 Mercedes-Benz GLE450 AMG-Line with AIRMATIC air suspension and E-Active Body Control. 64-color ambient lighting, Burmester 3D surround sound, and MBUX infotainment with Hey Mercedes AI assistant."},
    
    {"make": "Mercedes-Benz", "model": "C300 AMG Sport", "year": 2022, "price": 58000000, "mileage": 19000,
     "condition": "foreign_used", "transmission": "automatic", "fuel_type": "petrol",
     "body_type": "sedan", "engine": "2.0L Turbo", "exterior_color": "Polar White",
     "interior_color": "Black AMG Nappa Leather", "location": "Victoria Island, Lagos", "status": "available",
     "is_featured": False,
     "description": "2022 Mercedes-Benz C300 AMG Sport with 9G-TRONIC automatic gearbox. MBUX Hyperscreen option, augmented reality navigation, and standard AMG body kit and sport exhaust."},
    
    {"make": "Mercedes-Benz", "model": "E350 AMG Line", "year": 2020, "price": 52000000, "mileage": 38000,
     "condition": "foreign_used", "transmission": "automatic", "fuel_type": "petrol",
     "body_type": "sedan", "engine": "2.0L Turbo", "exterior_color": "Obsidian Black",
     "interior_color": "Macchiato Beige Leather", "location": "Maitama, Abuja", "status": "available",
     "is_featured": False,
     "description": "2020 Mercedes-Benz E350 AMG-Line in immaculate condition. Widescreen MBUX cockpit, Burmester surround sound, ENERGIZING comfort package, and comprehensive driver assistance system."},
    
    # BMW
    {"make": "BMW", "model": "X5 xDrive40i", "year": 2022, "price": 82000000, "mileage": 16000,
     "condition": "foreign_used", "transmission": "automatic", "fuel_type": "petrol",
     "body_type": "suv", "engine": "3.0L TwinPower Turbo", "exterior_color": "Carbon Black Metallic",
     "interior_color": "Cognac Leather Merino", "location": "Lekki, Lagos", "status": "available",
     "is_featured": True,
     "description": "2022 BMW X5 xDrive40i M-Sport Package with 22-inch M alloy wheels. Bowers & Wilkins Diamond surround sound, panoramic sky lounge LED roof, and xOffroad package with all-terrain mode."},
    
    {"make": "BMW", "model": "5 Series 530i M-Sport", "year": 2021, "price": 55000000, "mileage": 27000,
     "condition": "foreign_used", "transmission": "automatic", "fuel_type": "petrol",
     "body_type": "sedan", "engine": "2.0L TwinPower Turbo", "exterior_color": "Portimao Blue",
     "interior_color": "Vernasca Leather Black", "location": "Garki, Abuja", "status": "available",
     "is_featured": False,
     "description": "2021 BMW 530i M-Sport with gesture control and Curved Display infotainment. Shadow line package, adaptive LED headlights, BMW Live Cockpit Professional, and active protection system."},

    # Honda
    {"make": "Honda", "model": "Pilot TrailSport", "year": 2023, "price": 38000000, "mileage": 12000,
     "condition": "foreign_used", "transmission": "automatic", "fuel_type": "petrol",
     "body_type": "suv", "engine": "3.5L V6", "exterior_color": "Sonic Gray Pearl",
     "interior_color": "Black Water-Resistant", "location": "Ikeja, Lagos", "status": "available",
     "is_featured": False,
     "description": "2023 Honda Pilot TrailSport with standard AWD and terrain management system. Water-resistant interior materials, roof-mounted antenna, i-VTM4 torque-vectoring AWD, and hands-free tailgate."},
    
    {"make": "Honda", "model": "Accord Sport", "year": 2022, "price": 22000000, "mileage": 31000,
     "condition": "foreign_used", "transmission": "cvt", "fuel_type": "petrol",
     "body_type": "sedan", "engine": "1.5L Turbo VTEC", "exterior_color": "Sonic Gray Pearl",
     "interior_color": "Black Sport Leather", "location": "Lekki, Lagos", "status": "available",
     "is_featured": False,
     "description": "2022 Honda Accord Sport 2.0T with 10-speed automatic. Sport exterior accents, 19-inch sport alloy wheels, 10-inch touchscreen, wireless Apple CarPlay, and Honda Sensing safety suite."},

    # Hyundai
    {"make": "Hyundai", "model": "Palisade Calligraphy", "year": 2022, "price": 42000000, "mileage": 29000,
     "condition": "foreign_used", "transmission": "automatic", "fuel_type": "petrol",
     "body_type": "suv", "engine": "3.8L V6", "exterior_color": "Moonlight Cloud",
     "interior_color": "Beige Nappa Leather", "location": "Victoria Island, Lagos", "status": "available",
     "is_featured": False,
     "description": "2022 Hyundai Palisade Calligraphy AWD — Hyundai's flagship 8-seat luxury SUV. Nappa leather throughout, 12.3-inch infotainment, rear relaxation seats with massage function, and comprehensive HTRAC AWD."},
    
    {"make": "Hyundai", "model": "Tucson N-Line", "year": 2023, "price": 28000000, "mileage": 14000,
     "condition": "foreign_used", "transmission": "automatic", "fuel_type": "petrol",
     "body_type": "suv", "engine": "2.5L Theta III", "exterior_color": "Shimmering Silver",
     "interior_color": "Black N-Line Cloth/Leather", "location": "Ikeja, Lagos", "status": "available",
     "is_featured": False,
     "description": "2023 Hyundai Tucson N-Line with distinctive parametric exterior design. N-Line sport interior, 10.25-inch navigation, Bose premium audio, and Hyundai SmartSense safety system."},

    # Kia
    {"make": "Kia", "model": "Telluride EX", "year": 2022, "price": 40000000, "mileage": 33000,
     "condition": "foreign_used", "transmission": "automatic", "fuel_type": "petrol",
     "body_type": "suv", "engine": "3.8L V6 GDI", "exterior_color": "Snow White Pearl",
     "interior_color": "Nappa Leather Black", "location": "Lekki, Lagos", "status": "available",
     "is_featured": False,
     "description": "2022 Kia Telluride EX AWD. America's best 3-row SUV with luxurious appointments. 10.25-inch navigation, Harman Kardon premium audio, wireless charging, and Highway Driving Assist II."},

    # Ford
    {"make": "Ford", "model": "Explorer ST", "year": 2021, "price": 36000000, "mileage": 44000,
     "condition": "foreign_used", "transmission": "automatic", "fuel_type": "petrol",
     "body_type": "suv", "engine": "3.0L EcoBoost V6", "exterior_color": "Rapid Red Metallic",
     "interior_color": "Ebony ActiveX Leather", "location": "Port Harcourt", "status": "available",
     "is_featured": False,
     "description": "2021 Ford Explorer ST — the performance-oriented family SUV. 400hp twin-scroll turbocharged V6, adaptive suspension, Brembo front brakes, and ST-specific Ebony leather with red contrast stitching."},

    # Nissan
    {"make": "Nissan", "model": "Armada Platinum", "year": 2022, "price": 48000000, "mileage": 26000,
     "condition": "foreign_used", "transmission": "automatic", "fuel_type": "petrol",
     "body_type": "suv", "engine": "5.6L V8", "exterior_color": "Midnight Blue",
     "interior_color": "Almond Semi-Aniline Leather", "location": "Maitama, Abuja", "status": "available",
     "is_featured": False,
     "description": "2022 Nissan Armada Platinum 4WD — full-size luxury SUV with body-on-frame construction. Bose 13-speaker premium audio, captain's chairs, heated/cooled front and rear seats, and 12.3-inch digital cockpit."},

    # Land Rover
    {"make": "Land Rover", "model": "Range Rover Sport HSE Dynamic", "year": 2021, "price": 95000000, "mileage": 20000,
     "condition": "foreign_used", "transmission": "automatic", "fuel_type": "petrol",
     "body_type": "suv", "engine": "5.0L Supercharged V8", "exterior_color": "Firenze Red",
     "interior_color": "Ebony Windsor Leather", "location": "Ikoyi, Lagos", "status": "available",
     "is_featured": True,
     "description": "2021 Range Rover Sport HSE Dynamic Supercharged V8. Electronic air suspension with Terrain Response 2, Pixel Laser LED headlights, Pivi Pro infotainment with dual 11.4-inch screens, and Wade Sensing for river crossings."},
    
    {"make": "Land Rover", "model": "Defender 110 X", "year": 2022, "price": 88000000, "mileage": 15000,
     "condition": "foreign_used", "transmission": "automatic", "fuel_type": "petrol",
     "body_type": "suv", "engine": "3.0L I6 Supercharged", "exterior_color": "Eiger Grey",
     "interior_color": "Ebony/Khaki Windsor Leather", "location": "Lekki, Lagos", "status": "available",
     "is_featured": False,
     "description": "2022 Land Rover Defender 110 X — the ultimate expedition vehicle with luxury appointments. 5+2 seating, Extended Ground Clearance Package, Wade Sensing, and Meridian 700W surround sound system."},

    # Volkswagen
    {"make": "Volkswagen", "model": "Touareg Elegance", "year": 2021, "price": 45000000, "mileage": 32000,
     "condition": "foreign_used", "transmission": "automatic", "fuel_type": "petrol",
     "body_type": "suv", "engine": "3.0L TSI", "exterior_color": "Platinum Grey",
     "interior_color": "Nappa Leather Deep Black", "location": "Lekki, Lagos", "status": "available",
     "is_featured": False,
     "description": "2021 Volkswagen Touareg Elegance with Innovision Cockpit. 12-inch instrument cluster + 15-inch infotainment display, 4MOTION AWD, four-zone climate, and Dynaudio premium audio. German precision at its finest."},

    # Audi
    {"make": "Audi", "model": "Q7 Quattro Premium Plus", "year": 2022, "price": 78000000, "mileage": 17000,
     "condition": "foreign_used", "transmission": "automatic", "fuel_type": "petrol",
     "body_type": "suv", "engine": "3.0L TFSI V6", "exterior_color": "Navarra Blue Metallic",
     "interior_color": "Valcona Leather Okapi Brown", "location": "Victoria Island, Lagos", "status": "available",
     "is_featured": False,
     "description": "2022 Audi Q7 55 TFSI Quattro Premium Plus. 3-row luxury SUV with Virtual Cockpit Plus, Bang & Olufsen 3D sound, 10.1-inch MMI touch response, adaptive air suspension, and HD Matrix LED headlights."},

    # Jeep
    {"make": "Jeep", "model": "Grand Cherokee Overland", "year": 2022, "price": 52000000, "mileage": 23000,
     "condition": "foreign_used", "transmission": "automatic", "fuel_type": "petrol",
     "body_type": "suv", "engine": "3.6L Pentastar V6", "exterior_color": "Rocky Mountain Bronze",
     "interior_color": "Palomino Leather", "location": "Port Harcourt", "status": "available",
     "is_featured": False,
     "description": "2022 Jeep Grand Cherokee Overland with Quadra-Lift air suspension. McIntosh 19-speaker audio system, dual panoramic sunroof, head-up display, Night Vision camera, and Advanced ProTech Group package."},

    # Peugeot
    {"make": "Peugeot", "model": "3008 GT", "year": 2022, "price": 26000000, "mileage": 28000,
     "condition": "foreign_used", "transmission": "automatic", "fuel_type": "petrol",
     "body_type": "suv", "engine": "1.6L THP", "exterior_color": "Vertigo Blue",
     "interior_color": "GT Black Alcantara/Leather", "location": "Enugu", "status": "available",
     "is_featured": False,
     "description": "2022 Peugeot 3008 GT with i-Cockpit design. 12.3-inch 3D digital instrument cluster, 10-inch infotainment, drive mode selector, and distinctive French design flair that stands out on Nigerian roads."},

    # Nigerian-Used vehicles
    {"make": "Toyota", "model": "Venza XLE", "year": 2020, "price": 19500000, "mileage": 72000,
     "condition": "nigerian_used", "transmission": "automatic", "fuel_type": "hybrid",
     "body_type": "suv", "engine": "2.5L Hybrid", "exterior_color": "Blueprint Blue",
     "interior_color": "Macadamia Leather", "location": "Ikeja, Lagos", "status": "available",
     "is_featured": False,
     "description": "2020 Toyota Venza XLE Hybrid - a one-owner Nigerian-used vehicle in excellent mechanical and aesthetic condition. Full Toyota Safety Sense and JBL 9-speaker audio. Complete service records."},
    
    {"make": "Honda", "model": "CR-V EX-L", "year": 2021, "price": 15000000, "mileage": 85000,
     "condition": "nigerian_used", "transmission": "cvt", "fuel_type": "petrol",
     "body_type": "suv", "engine": "1.5L Turbo VTEC", "exterior_color": "Modern Steel",
     "interior_color": "Gray Leather", "location": "Abuja", "status": "available",
     "is_featured": False,
     "description": "2021 Honda CR-V EX-L (Nigerian used). Maintained by a single owner with meticulous service history. Power moonroof, heated seats, wireless CarPlay, and Honda Sensing driver-assist suite. Clean title."},

    # Sold vehicles (for admin demonstration)
    {"make": "Toyota", "model": "Sienna XSE", "year": 2022, "price": 52000000, "mileage": 30000,
     "condition": "foreign_used", "transmission": "automatic", "fuel_type": "hybrid",
     "body_type": "van", "engine": "2.5L Hybrid", "exterior_color": "Midnight Black Metallic",
     "interior_color": "Black Leather", "location": "Lekki, Lagos", "status": "sold",
     "is_featured": False,
     "description": "SOLD — 2022 Toyota Sienna XSE Premium AWD Hybrid. Tri-zone automatic climate, in-floor storage, power-folding 3rd row, 18-inch alloy wheels, and JBL 12-speaker audio."},
]

SAMPLE_FEATURES = [
    "Air Conditioning",
    "Leather Seats",
    "Reverse Camera",
    "Parking Sensors",
    "Sunroof / Moonroof",
    "Navigation System",
    "Bluetooth Connectivity",
    "Apple CarPlay",
    "Android Auto",
    "Cruise Control",
    "Keyless Entry",
    "Push-Button Start",
    "ABS Brakes",
    "Front & Side Airbags",
    "Heated Seats",
    "Ventilated Seats",
    "Wireless Charging",
    "Ambient Lighting",
    "Heads-Up Display",
    "Lane Keep Assist",
    "Blind Spot Monitor",
    "Adaptive Cruise Control",
    "3rd Row Seating",
    "Panoramic Sunroof",
    "Premium Audio System",
    "Power Liftgate",
    "AWD / 4WD",
    "Off-Road Package",
]

SAMPLE_TESTIMONIALS = [
    {
        "name": "Chukwuemeka Obi", "location": "Lekki Phase 1, Lagos",
        "vehicle_purchased": "2021 Toyota Camry XSE", "rating": 5,
        "comment": "Samko Cars exceeded every expectation. The vehicle was exactly as described, full documentation provided, and the transfer process was seamless. I drove home with confidence. Highly recommended to anyone looking for a trusted dealership in Lagos."
    },
    {
        "name": "Adaobi Nwosu", "location": "Maitama, Abuja",
        "vehicle_purchased": "2022 Lexus RX350 F-Sport", "rating": 5,
        "comment": "I was nervous buying a high-value vehicle online but Samko Cars made everything transparent. The car arrived in showroom condition. The WhatsApp communication was fast and professional throughout the entire process."
    },
    {
        "name": "Ibrahim Mustapha", "location": "Garki, Abuja",
        "vehicle_purchased": "2020 Mercedes-Benz GLE450", "rating": 5,
        "comment": "Outstanding professionalism from start to finish. The vehicle inspection report was thorough, pricing was competitive, and there were no hidden charges. This is what Nigerian car buying should look like."
    },
    {
        "name": "Funmilayo Adeyemi", "location": "Victoria Island, Lagos",
        "vehicle_purchased": "2022 BMW X5 M-Sport", "rating": 5,
        "comment": "I have bought 3 vehicles from Samko Cars now. Each time the experience is better than the last. Trustworthy, responsive, and genuinely committed to customer satisfaction. My forever dealership."
    },
    {
        "name": "Emmanuel Eze", "location": "Port Harcourt, Rivers",
        "vehicle_purchased": "2021 Toyota Highlander XLE", "rating": 4,
        "comment": "Great service, excellent vehicle selection, and honest pricing. The team answered all my questions patiently. Minor delay in paperwork but they communicated every step. Very satisfied overall."
    },
    {
        "name": "Ngozi Okonkwo", "location": "Enugu",
        "vehicle_purchased": "2022 Hyundai Palisade Calligraphy", "rating": 5,
        "comment": "I searched many dealerships before finding Samko Cars. The difference is the authenticity — every vehicle is genuinely verified. My Palisade is perfect. The family loves it. Thank you, Samko Cars!"
    },
]

SAMPLE_SOCIALS = [
    {"platform": "instagram", "platform_name": "Instagram", "url": "https://www.instagram.com/samkocars", "order": 1},
    {"platform": "facebook", "platform_name": "Facebook", "url": "https://www.facebook.com/samkocars", "order": 2},
    {"platform": "tiktok", "platform_name": "TikTok", "url": "https://www.tiktok.com/@samkocars", "order": 3},
    {"platform": "twitter", "platform_name": "X (Twitter)", "url": "https://x.com/samkocars", "order": 4},
    {"platform": "youtube", "platform_name": "YouTube", "url": "https://www.youtube.com/@samkocars", "order": 5},
]


def generate_svg_placeholder(year, make, model, body_type, color):
    """
    Generate a styled SVG placeholder image for a vehicle.
    Each car gets a unique look based on its attributes.
    """
    color_map = {
        "black": "#1a1a1a", "white": "#f5f5f5", "silver": "#c0c0c0", "grey": "#808080",
        "gray": "#808080", "blue": "#1e3a5f", "red": "#8b0000", "green": "#1a4a1a",
        "beige": "#c8b99a", "brown": "#5c3d2e", "orange": "#cc5500", "yellow": "#b8a000",
        "gold": "#b8860b", "pearl": "#f2f0e8", "graphite": "#3a3a3a",
    }
    
    bg_color = "#2d3748"
    for key, val in color_map.items():
        if key in color.lower():
            bg_color = val
            break

    text_lines = [make, model, str(year)]
    
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 500" width="800" height="500">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:{bg_color};stop-opacity:1" />
      <stop offset="100%" style="stop-color:#0a0a0a;stop-opacity:1" />
    </linearGradient>
    <linearGradient id="carGrad" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" style="stop-color:#ffffff;stop-opacity:0.35" />
      <stop offset="100%" style="stop-color:#000000;stop-opacity:0.1" />
    </linearGradient>
    <filter id="glow">
      <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
      <feMerge><feMergeNode in="coloredBlur"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
  </defs>
  
  <!-- Background -->
  <rect width="800" height="500" fill="url(#bg)"/>
  
  <!-- Grid pattern -->
  <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
    <path d="M 40 0 L 0 0 0 40" fill="none" stroke="white" stroke-width="0.3" opacity="0.1"/>
  </pattern>
  <rect width="800" height="500" fill="url(#grid)"/>
  
  <!-- Car silhouette - simplified SUV/Sedan shape -->
  <g transform="translate(150, 240)">
    <!-- Shadow -->
    <ellipse cx="250" cy="175" rx="240" ry="18" fill="black" opacity="0.5"/>
    
    <!-- Body -->
    <rect x="30" y="100" width="440" height="80" rx="8" fill="{bg_color}" stroke="rgba(255,255,255,0.25)" stroke-width="2"/>
    <rect x="0" y="148" width="500" height="32" rx="6" fill="{bg_color}" stroke="rgba(255,255,255,0.2)" stroke-width="1.5"/>
    
    <!-- Roof -->
    <path d="M 90 100 C 110 55, 160 40, 250 38 C 330 36, 380 50, 420 100 Z" 
          fill="{bg_color}" stroke="rgba(255,255,255,0.3)" stroke-width="2"/>
    
    <!-- Windows -->
    <path d="M 115 98 C 125 65, 155 52, 240 50 L 240 96 Z" 
          fill="rgba(120,200,255,0.5)" stroke="rgba(255,255,255,0.5)" stroke-width="1.5"/>
    <path d="M 245 50 L 370 55 C 400 65, 415 82, 415 98 L 245 96 Z" 
          fill="rgba(120,200,255,0.5)" stroke="rgba(255,255,255,0.5)" stroke-width="1.5"/>
    
    <!-- A/B pillars -->
    <line x1="240" y1="50" x2="243" y2="98" stroke="rgba(255,255,255,0.6)" stroke-width="3"/>
    
    <!-- Wheels -->
    <circle cx="100" cy="175" r="42" fill="#1a1a1a" stroke="#555" stroke-width="3"/>
    <circle cx="100" cy="175" r="28" fill="#333" stroke="#888" stroke-width="2"/>
    <circle cx="100" cy="175" r="12" fill="#aaa" stroke="#ccc" stroke-width="1"/>
    
    <circle cx="400" cy="175" r="42" fill="#1a1a1a" stroke="#555" stroke-width="3"/>
    <circle cx="400" cy="175" r="28" fill="#333" stroke="#888" stroke-width="2"/>
    <circle cx="400" cy="175" r="12" fill="#aaa" stroke="#ccc" stroke-width="1"/>
    
    <!-- Headlights -->
    <rect x="455" y="118" width="38" height="14" rx="4" fill="rgba(255,240,180,0.9)" stroke="rgba(255,255,150,0.8)" stroke-width="1" filter="url(#glow)"/>
    <!-- Tail lights -->
    <rect x="8" y="118" width="30" height="14" rx="4" fill="rgba(255,60,60,0.9)" stroke="rgba(255,100,100,0.8)" stroke-width="1"/>
    
    <!-- Highlight -->
    <path d="M 80 85 C 180 60, 330 58, 420 80" stroke="rgba(255,255,255,0.5)" stroke-width="2" fill="none"/>
  </g>
  
  <!-- Brand logo area -->
  <circle cx="400" cy="60" r="32" fill="none" stroke="rgba(255,255,255,0.3)" stroke-width="1.5"/>
  <text x="400" y="68" text-anchor="middle" fill="white" font-family="Georgia, serif" font-size="20" font-weight="bold" opacity="0.7">S</text>
  
  <!-- Vehicle info text -->
  <text x="400" y="420" text-anchor="middle" fill="rgba(255,255,255,0.95)" font-family="'Segoe UI', Arial, sans-serif" font-size="28" font-weight="700" letter-spacing="2">
    {make.upper()}
  </text>
  <text x="400" y="450" text-anchor="middle" fill="rgba(255,255,255,0.7)" font-family="'Segoe UI', Arial, sans-serif" font-size="18" font-weight="400" letter-spacing="1">
    {model} &bull; {year}
  </text>
  
  <!-- Samko Cars watermark -->
  <text x="20" y="485" fill="rgba(255,255,255,0.3)" font-family="'Segoe UI', Arial, sans-serif" font-size="12">SAMKO CARS</text>
</svg>"""
    return svg


class Command(BaseCommand):
    help = 'Seed Samko Cars database with realistic demo vehicle inventory, features, testimonials, and sample settings.'

    def add_arguments(self, parser):
        parser.add_argument('--clear', action='store_true', help='Delete all existing vehicle data before seeding')
        parser.add_argument('--quiet', action='store_true', help='Suppress verbose output')

    def handle(self, *args, **options):
        quiet = options.get('quiet', False)

        if options.get('clear'):
            Car.objects.all().delete()
            Feature.objects.all().delete()
            Testimonial.objects.all().delete()
            SocialMedia.objects.all().delete()
            if not quiet:
                self.stdout.write(self.style.WARNING('Cleared existing inventory, features, testimonials, and social links.'))

        # Only seed if database is empty (for build.sh auto-seed safety)
        car_count = Car.objects.count()
        if car_count > 0 and not options.get('clear'):
            if not quiet:
                self.stdout.write(self.style.SUCCESS(f'Database already has {car_count} vehicles. Skipping seed. Use --clear to re-seed.'))
            return

        # ── Features ──────────────────────────────────────────────────────────
        if not quiet:
            self.stdout.write('Creating vehicle features...')
        feature_objects = {}
        for feature_name in SAMPLE_FEATURES:
            feature, _ = Feature.objects.get_or_create(name=feature_name)
            feature_objects[feature_name] = feature

        # ── Site Settings ─────────────────────────────────────────────────────
        SiteSetting.get_settings()  # creates defaults if not present
        if not quiet:
            self.stdout.write('Site settings initialized.')

        # ── Social Media ──────────────────────────────────────────────────────
        if SocialMedia.objects.count() == 0:
            for social in SAMPLE_SOCIALS:
                SocialMedia.objects.create(**social)
            if not quiet:
                self.stdout.write('Social media links created.')

        # ── Testimonials ──────────────────────────────────────────────────────
        if Testimonial.objects.count() == 0:
            for i, t in enumerate(SAMPLE_TESTIMONIALS):
                Testimonial.objects.create(order=i, **t)
            if not quiet:
                self.stdout.write('Testimonials created.')

        # ── Vehicles ──────────────────────────────────────────────────────────
        if not quiet:
            self.stdout.write(f'Seeding {len(SAMPLE_VEHICLES)} sample vehicles with SVG placeholder images...')

        created_count = 0
        for vehicle_data in SAMPLE_VEHICLES:
            features_for_car = vehicle_data.pop('features', None)
            try:
                car = Car.objects.create(**vehicle_data)

                # Assign 4–8 random features
                feature_names = random.sample(list(feature_objects.keys()), k=min(8, len(feature_objects)))
                # Always include some key ones
                base_features = ["Air Conditioning", "Reverse Camera", "Bluetooth Connectivity"]
                for f in base_features:
                    if f in feature_objects:
                        feature_names.append(f)
                car.features.set([feature_objects[f] for f in set(feature_names) if f in feature_objects])

                # Generate and save SVG placeholder image as the cover
                svg_content = generate_svg_placeholder(
                    car.year, car.make, car.model, car.body_type, car.exterior_color
                )
                from apps.cars.models import CarImage
                img_file = ContentFile(svg_content.encode('utf-8'), name=f"{car.slug}-cover.svg")
                CarImage.objects.create(car=car, image=img_file, is_cover=True, order=0, caption=f"{car.year} {car.make} {car.model} - Main View")
                
                # Create 2 additional angle SVGs
                for angle_idx, angle_name in enumerate(["side-view", "rear-view"], start=1):
                    svg2 = generate_svg_placeholder(car.year, car.make, car.model, car.body_type, car.exterior_color)
                    img2 = ContentFile(svg2.encode('utf-8'), name=f"{car.slug}-{angle_name}.svg")
                    CarImage.objects.create(car=car, image=img2, is_cover=False, order=angle_idx, caption=f"{car.year} {car.make} {car.model} - {angle_name.replace('-', ' ').title()}")

                created_count += 1
                if not quiet:
                    safe_price = f"NGN {int(car.price):,}"
                    self.stdout.write(f'  [OK] {car}  |  {safe_price}  |  {car.get_status_display()}')

            except Exception as e:
                self.stdout.write(self.style.ERROR(f'  [ERROR] Error creating vehicle: {vehicle_data.get("make", "?")} {vehicle_data.get("model", "?")} - {str(e).encode("ascii", "replace").decode()}'))

        if not quiet:
            self.stdout.write(self.style.SUCCESS(
                f'\n[SUCCESS] Samko Cars seeding complete!\n'
                f'   {created_count} vehicles created\n'
                f'   {len(feature_objects)} features loaded\n'
                f'   {len(SAMPLE_TESTIMONIALS)} testimonials added\n'
                f'   {len(SAMPLE_SOCIALS)} social links created\n\n'
                f'Create your admin account with:\n'
                f'   python manage.py createsuperuser\n'
            ))
        else:
            self.stdout.write(self.style.SUCCESS(f'Seeded {created_count} vehicles successfully.'))
