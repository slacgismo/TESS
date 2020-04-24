

class Utility(db.Model):
    
    __tablename__ = 'utilities'

    utility_id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
    name = db.Column(db.String(64), nullable=False)
    subscription_start = db.Column(TIMESTAMP, nullable=False)
    subscription_end = db.Column(TIMESTAMP, nullable=False)

    def __repr__(self):
        return f'<Utility utility_id={self.utility_id} name={self.name}>'