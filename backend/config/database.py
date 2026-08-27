import logging
from pymongo import MongoClient, ASCENDING
from config.settings import settings

logger = logging.getLogger("ai_krishi_mitra.db")

class Database:
    client: MongoClient = None
    db = None

    def connect(self):
        try:
            self.client = MongoClient(settings.MONGODB_URI, serverSelectionTimeoutMS=5000)
            self.db = self.client[settings.DATABASE_NAME]
            # Ping database to confirm connection
            self.client.admin.command('ping')
            logger.info(f"Connected to MongoDB successfully: {settings.DATABASE_NAME}")
            self.create_indexes()
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise e

    def close(self):
        if self.client:
            self.client.close()
            logger.info("Closed MongoDB connection.")

    def create_indexes(self):
        try:
            # Farmers: unique email and mobile
            self.db.farmers.create_index([("email", ASCENDING)], unique=True, sparse=True)
            self.db.farmers.create_index([("mobile", ASCENDING)], unique=True)
            self.db.farmers.create_index([("farmerId", ASCENDING)], unique=True)

            # Crops: index on farmerId and cropId
            self.db.crops.create_index([("farmerId", ASCENDING)])
            self.db.crops.create_index([("cropId", ASCENDING)], unique=True)

            # Land: index on farmerId
            self.db.land_records.create_index([("farmerId", ASCENDING)])

            # Procurement applications: index on applicationId, procurementId, farmerId
            self.db.procurement_applications.create_index([("applicationId", ASCENDING)], unique=True)
            self.db.procurement_applications.create_index([("procurementId", ASCENDING)], unique=True)
            self.db.procurement_applications.create_index([("farmerId", ASCENDING)])

            # Procurement centres
            self.db.procurement_centres.create_index([("centreId", ASCENDING)], unique=True)

            # Bank accounts: index on farmerId and bankAccountId
            self.db.bank_accounts.create_index([("bankAccountId", ASCENDING)], unique=True)
            self.db.bank_accounts.create_index([("farmerId", ASCENDING)])

            # Payments: index on paymentId, procurementId, farmerId
            self.db.payments.create_index([("paymentId", ASCENDING)], unique=True)
            self.db.payments.create_index([("procurementId", ASCENDING)])
            self.db.payments.create_index([("farmerId", ASCENDING)])

            # Disease Analyses
            self.db.disease_analyses.create_index([("farmerId", ASCENDING)])
            self.db.disease_analyses.create_index([("analysisId", ASCENDING)], unique=True)

            # Market & Buyers
            self.db.market_prices.create_index([("crop", ASCENDING)])
            self.db.buyers.create_index([("buyerId", ASCENDING)], unique=True)

            logger.info("MongoDB indexes verified successfully.")
        except Exception as e:
            logger.warning(f"Error creating indexes: {e}")

    # Convenience collection accessors
    @property
    def farmers(self):
        return self.db.farmers

    @property
    def crops(self):
        return self.db.crops

    @property
    def land_records(self):
        return self.db.land_records

    @property
    def procurement_centres(self):
        return self.db.procurement_centres

    @property
    def procurement_applications(self):
        return self.db.procurement_applications

    @property
    def bank_accounts(self):
        return self.db.bank_accounts

    @property
    def payments(self):
        return self.db.payments

    @property
    def ai_recommendations(self):
        return self.db.ai_recommendations

    @property
    def disease_analyses(self):
        return self.db.disease_analyses

    @property
    def market_prices(self):
        return self.db.market_prices

    @property
    def buyers(self):
        return self.db.buyers

db_manager = Database()

def get_database():
    return db_manager
