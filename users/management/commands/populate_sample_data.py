from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

from users.models import Company
from patients.models import Patient
from vehicles.models import Vehicle
from trips.models import Trip, ChatMessage
from ems.models import EMSReport
from billing.models import Invoice, Contract, SystemSettings

User = get_user_model()


class Command(BaseCommand):
    help = 'Populates the database with sample data for testing'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Clearing existing sample data...'))
        self.clear_data()
        
        self.stdout.write(self.style.SUCCESS('Creating sample data...'))
        
        # Create companies
        companies = self.create_companies()
        
        # Create users
        users = self.create_users()
        
        # Create patients
        patients = self.create_patients(companies)
        
        # Create vehicles
        vehicles = self.create_vehicles(companies)
        
        # Create trips
        trips = self.create_trips(patients, vehicles, users)
        
        # Create chat messages
        self.create_chat_messages(trips, users)
        
        # Create EMS reports
        self.create_ems_reports(trips)
        
        # Create invoices and contracts
        self.create_billing_data(trips, companies)
        
        # Create system settings
        self.create_system_settings()
        
        self.stdout.write(self.style.SUCCESS('✅ Sample data created successfully!'))
        self.print_summary()

    def clear_data(self):
        """Clear all existing data"""
        ChatMessage.objects.all().delete()
        EMSReport.objects.all().delete()
        Invoice.objects.all().delete()
        Contract.objects.all().delete()
        Trip.objects.all().delete()
        Patient.objects.all().delete()
        Vehicle.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()
        Company.objects.all().delete()
        SystemSettings.objects.all().delete()

    def create_companies(self):
        self.stdout.write('Creating companies...')
        companies = {
            'clients': [],
            'vendors': []
        }
        
        # Client companies
        companies['clients'].append(Company.objects.create(
            company_name='Metro Healthcare',
            company_type='client',
            contact_person='Sarah Johnson',
            phone_number='+20-123-456-7890',
            email='contact@metrohealthcare.com',
            address='123 Medical Plaza, Cairo, Egypt',
            status='active'
        ))
        
        companies['clients'].append(Company.objects.create(
            company_name='City General Hospital',
            company_type='client',
            contact_person='Dr. Ahmed Hassan',
            phone_number='+20-123-456-7891',
            email='info@citygeneralhospital.com',
            address='456 Hospital Road, Alexandria, Egypt',
            status='active'
        ))
        
        # Vendor companies
        companies['vendors'].append(Company.objects.create(
            company_name='Express Medical Transport',
            company_type='vendor',
            contact_person='Mohamed Ali',
            phone_number='+20-123-456-7892',
            email='dispatch@expressmedical.com',
            address='789 Transport Ave, Cairo, Egypt',
            status='active'
        ))
        
        companies['vendors'].append(Company.objects.create(
            company_name='Elite Ambulance Services',
            company_type='vendor',
            contact_person='Fatima Ibrahim',
            phone_number='+20-123-456-7893',
            email='contact@eliteambulance.com',
            address='321 Emergency Blvd, Giza, Egypt',
            status='active'
        ))
        
        self.stdout.write(self.style.SUCCESS(f'  Created {len(companies["clients"])} client companies'))
        self.stdout.write(self.style.SUCCESS(f'  Created {len(companies["vendors"])} vendor companies'))
        
        return companies

    def create_users(self):
        self.stdout.write('Creating users...')
        users = {
            'admin': [],
            'drivers': [],
            'paramedics': [],
            'corporate': [],
            'vendor': []
        }
        
        # Admin user - check if already exists
        admin_user = User.objects.filter(username='admin').first()
        if admin_user:
            users['admin'].append(admin_user)
            self.stdout.write(self.style.WARNING('  Admin user already exists, skipping creation'))
        else:
            users['admin'].append(User.objects.create_user(
                username='admin',
                email='admin@atw.com',
                password='admin123',
                role='Admin',
                status='active',
                first_name='System',
                last_name='Administrator'
            ))
        
        
        # Drivers
        for i, name in enumerate([('Khaled', 'Mohamed'), ('Omar', 'Hassan'), ('Youssef', 'Ahmed')], 1):
            users['drivers'].append(User.objects.create_user(
                username=f'driver{i}',
                email=f'driver{i}@atw.com',
                password='driver123',
                role='Driver',
                status='active',
                first_name=name[0],
                last_name=name[1],
                phone_number=f'+20-100-000-000{i}'
            ))
        
        # Paramedics
        for i, name in enumerate([('Amira', 'Salem'), ('Layla', 'Farid'), ('Nour', 'Kamel')], 1):
            users['paramedics'].append(User.objects.create_user(
                username=f'paramedic{i}',
                email=f'paramedic{i}@atw.com',
                password='paramedic123',
                role='Paramedic',
                status='active',
                first_name=name[0],
                last_name=name[1],
                phone_number=f'+20-110-000-000{i}'
            ))
        
        # Corporate users
        for i, name in enumerate([('Sarah', 'Johnson'), ('Ahmed', 'Hassan')], 1):
            users['corporate'].append(User.objects.create_user(
                username=f'corporate{i}',
                email=f'corporate{i}@atw.com',
                password='corporate123',
                role='Corporate',
                status='active',
                first_name=name[0],
                last_name=name[1],
                phone_number=f'+20-120-000-000{i}'
            ))
        
        # Vendor users
        for i, name in enumerate([('Mohamed', 'Ali'), ('Fatima', 'Ibrahim')], 1):
            users['vendor'].append(User.objects.create_user(
                username=f'vendor{i}',
                email=f'vendor{i}@atw.com',
                password='vendor123',
                role='Vendor',
                status='active',
                first_name=name[0],
                last_name=name[1],
                phone_number=f'+20-130-000-000{i}'
            ))
        
        total = sum(len(v) for v in users.values())
        self.stdout.write(self.style.SUCCESS(f'  Created {total} users'))
        
        return users

    def create_patients(self, companies):
        self.stdout.write('Creating patients...')
        patients = []
        
        patient_data = [
            ('John Smith', '2021-MRN-001', '1965-03-15'),
            ('Emily Davis', '2021-MRN-002', '1978-07-22'),
            ('Michael Brown', '2021-MRN-003', '1952-11-30'),
            ('Lisa Anderson', '2021-MRN-004', '1990-05-18'),
            ('Robert Wilson', '2021-MRN-005', '1945-09-08'),
        ]
        
        for i, (name, mrn, dob) in enumerate(patient_data):
            company = companies['clients'][i % len(companies['clients'])]
            patients.append(Patient.objects.create(
                name=name,
                medical_record_number=mrn,
                dob=dob,
                company=company
            ))
        
        self.stdout.write(self.style.SUCCESS(f'  Created {len(patients)} patients'))
        
        return patients

    def create_vehicles(self, companies):
        self.stdout.write('Creating vehicles...')
        vehicles = []
        
        vehicle_data = [
            ('AMB-001', 'Mercedes-Benz Sprinter', 'Advanced'),
            ('AMB-002', 'Ford Transit', 'Basic'),
            ('AMB-003', 'Mercedes-Benz Sprinter', 'ICU'),
            ('AMB-004', 'Toyota Hiace', 'Basic'),
            ('AMB-005', 'Ford Transit', 'Advanced'),
            ('WC-001', 'Dodge Grand Caravan', 'Wheelchair'),
        ]
        
        for i, (plate, model, vtype) in enumerate(vehicle_data):
            company = companies['vendors'][i % len(companies['vendors'])]
            vehicles.append(Vehicle.objects.create(
                plate_number=plate,
                model=model,
                type=vtype,
                capacity=1 if vtype == 'Wheelchair' else 2,
                status='available',
                current_location='Cairo Station',
                odometer_reading=10000 + (i * 500),
                vendor_company=company
            ))
        
        self.stdout.write(self.style.SUCCESS(f'  Created {len(vehicles)} vehicles'))
        
        return vehicles

    def create_trips(self, patients, vehicles, users):
        self.stdout.write('Creating trips...')
        trips = []
        
        now = timezone.now()
        
        trip_data = [
            ('pending', None, None, 0, 0),
            ('assigned', None, None, 0, 0),
            ('en_route', now - timedelta(hours=2), None, 15234.5, 0),
            ('at_pickup', now - timedelta(hours=3), None, 15240.2, 0),
            ('in_transit', now - timedelta(hours=4), None, 15245.8, 0),
            ('arrived', now - timedelta(hours=5), None, 15267.3, 15267.3),
            ('completed', now - timedelta(days=1), now - timedelta(days=1) + timedelta(hours=1), 15100.0, 15125.5),
            ('completed', now - timedelta(days=2), now - timedelta(days=2) + timedelta(hours=2), 14900.0, 14935.2),
            ('completed', now - timedelta(days=3), now - timedelta(days=3) + timedelta(hours=1, minutes=30), 14700.0, 14728.8),
            ('cancelled', None, None, 0, 0),
        ]
        
        locations = [
            ('Cairo International Airport', 'Nile Hilton Hospital'),
            ('Metro Healthcare', 'City General Hospital'),
            ('Alexandria Station', 'Cairo Medical Center'),
            ('Giza Residence Complex', 'Metro Healthcare'),
            ('Downtown Plaza', 'Emergency Care Center'),
            ('Maadi District', 'Specialized Hospital'),
            ('Nasr City Clinic', 'Rehabilitation Center'),
            ('Heliopolis Medical', 'Metro Healthcare'),
            ('Zamalek Address', 'City General Hospital'),
            ('6th October City', 'Cairo Medical Center'),
        ]
        
        for i, (status, start_time, end_time, start_odo, end_odo) in enumerate(trip_data):
            patient = patients[i % len(patients)]
            vehicle = vehicles[i % len(vehicles)] if status != 'pending' else None
            driver = users['drivers'][i % len(users['drivers'])] if status not in ['pending', 'cancelled'] else None
            paramedic = users['paramedics'][i % len(users['paramedics'])] if status not in ['pending', 'cancelled'] else None
            
            trips.append(Trip.objects.create(
                patient=patient,
                vehicle=vehicle,
                driver=driver,
                paramedic=paramedic,
                start_location=locations[i][0],
                end_location=locations[i][1],
                status=status,
                start_time=start_time,
                end_time=end_time,
                start_odometer=start_odo if start_odo > 0 else None,
                end_odometer=end_odo if end_odo > 0 else None,
                request_source=['phone', 'online', 'app', 'contract'][i % 4]
            ))
        
        self.stdout.write(self.style.SUCCESS(f'  Created {len(trips)} trips'))
        
        return trips

    def create_chat_messages(self, trips, users):
        self.stdout.write('Creating chat messages...')
        messages = []
        
        # Create messages for trips that are in progress
        active_trips = [t for t in trips if t.status in ['assigned', 'en_route', 'at_pickup', 'in_transit']]
        
        for trip in active_trips:
            if trip.driver and trip.paramedic:
                # Driver -> Paramedic
                messages.append(ChatMessage.objects.create(
                    trip=trip,
                    sender=trip.driver,
                    receiver=trip.paramedic,
                    message_content='On the way to pickup location',
                    message_type='text'
                ))
                
                # Paramedic -> Driver
                messages.append(ChatMessage.objects.create(
                    trip=trip,
                    sender=trip.paramedic,
                    receiver=trip.driver,
                    message_content='Equipment checked and ready',
                    message_type='text'
                ))
        
        self.stdout.write(self.style.SUCCESS(f'  Created {len(messages)} chat messages'))
        
        return messages

    def create_ems_reports(self, trips):
        self.stdout.write('Creating EMS reports...')
        reports = []
        
        completed_trips = [t for t in trips if t.status == 'completed']
        
        medical_data_templates = [
            'Patient stable. Vital signs: BP 120/80, HR 72, O2 Sat 98%. No complications during transport.',
            'Patient required oxygen support. Vitals monitored throughout journey. Responded well to treatment.',
            'Routine transport. Patient comfortable. No medical interventions required during transfer.',
        ]
        
        for i, trip in enumerate(completed_trips):
            reports.append(EMSReport.objects.create(
                trip=trip,
                medical_data=medical_data_templates[i % len(medical_data_templates)]
            ))
        
        self.stdout.write(self.style.SUCCESS(f'  Created {len(reports)} EMS reports'))
        
        return reports

    def create_billing_data(self, trips, companies):
        self.stdout.write('Creating billing data...')
        invoices = []
        contracts = []
        
        # Create invoices for completed trips
        completed_trips = [t for t in trips if t.status == 'completed']
        
        for i, trip in enumerate(completed_trips):
            amount = Decimal('500.00') + (Decimal(trip.total_distance or 25) * Decimal('10.00'))
            tax = amount * Decimal('0.14')  # 14% tax
            
            invoices.append(Invoice.objects.create(
                trip=trip,
                company=trip.patient.company,
                amount=amount,
                tax=tax,
                status=['pending', 'paid'][i % 2],
                due_date=timezone.now() + timedelta(days=30)
            ))
        
        # Create contracts for all companies
        for company in companies['clients'] + companies['vendors']:
            contract_type = 'client' if company.company_type == 'client' else 'vendor'
            contracts.append(Contract.objects.create(
                company=company,
                contract_type=contract_type,
                start_date=timezone.now() - timedelta(days=180),
                end_date=timezone.now() + timedelta(days=185),
                status='active',
                terms_document_path=f'/contracts/{company.company_name.replace(" ", "_")}_contract.pdf'
            ))
        
        self.stdout.write(self.style.SUCCESS(f'  Created {len(invoices)} invoices'))
        self.stdout.write(self.style.SUCCESS(f'  Created {len(contracts)} contracts'))
        
        return invoices, contracts

    def create_system_settings(self):
        self.stdout.write('Creating system settings...')
        settings = []
        
        settings_data = [
            ('base_fare', '500.00', 'Base fare for all trips in EGP'),
            ('per_km_rate', '10.00', 'Rate per kilometer in EGP'),
            ('tax_rate', '0.14', 'Tax rate (14%)'),
            ('currency', 'EGP', 'System currency'),
            ('payment_terms_days', '30', 'Payment terms in days'),
        ]
        
        for key, value, description in settings_data:
            settings.append(SystemSettings.objects.create(
                setting_key=key,
                setting_value=value,
                description=description,
                is_active=True
            ))
        
        self.stdout.write(self.style.SUCCESS(f'  Created {len(settings)} system settings'))
        
        return settings

    def print_summary(self):
        self.stdout.write('\n' + '=' * 60)
        self.stdout.write(self.style.SUCCESS('SAMPLE DATA SUMMARY'))
        self.stdout.write('=' * 60)
        self.stdout.write(f'Companies: {Company.objects.count()}')
        self.stdout.write(f'  - Clients: {Company.objects.filter(company_type="client").count()}')
        self.stdout.write(f'  - Vendors: {Company.objects.filter(company_type="vendor").count()}')
        self.stdout.write(f'Users: {User.objects.count()}')
        self.stdout.write(f'  - Admins: {User.objects.filter(role="Admin").count()}')
        self.stdout.write(f'  - Drivers: {User.objects.filter(role="Driver").count()}')
        self.stdout.write(f'  - Paramedics: {User.objects.filter(role="Paramedic").count()}')
        self.stdout.write(f'  - Corporate: {User.objects.filter(role="Corporate").count()}')
        self.stdout.write(f'  - Vendors: {User.objects.filter(role="Vendor").count()}')
        self.stdout.write(f'Patients: {Patient.objects.count()}')
        self.stdout.write(f'Vehicles: {Vehicle.objects.count()}')
        self.stdout.write(f'Trips: {Trip.objects.count()}')
        self.stdout.write(f'  - Pending: {Trip.objects.filter(status="pending").count()}')
        self.stdout.write(f'  - In Progress: {Trip.objects.filter(status__in=["assigned", "en_route", "at_pickup", "in_transit", "arrived"]).count()}')
        self.stdout.write(f'  - Completed: {Trip.objects.filter(status="completed").count()}')
        self.stdout.write(f'  - Cancelled: {Trip.objects.filter(status="cancelled").count()}')
        self.stdout.write(f'Chat Messages: {ChatMessage.objects.count()}')
        self.stdout.write(f'EMS Reports: {EMSReport.objects.count()}')
        self.stdout.write(f'Invoices: {Invoice.objects.count()}')
        self.stdout.write(f'Contracts: {Contract.objects.count()}')
        self.stdout.write(f'System Settings: {SystemSettings.objects.count()}')
        self.stdout.write('=' * 60 + '\n')
