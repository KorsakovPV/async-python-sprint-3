from sqlalchemy import VARCHAR, Column, DateTime, sql, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import as_declarative
from sqlalchemy.orm import declared_attr
from sqlalchemy.sql import func
from sqlalchemy import BOOLEAN, INTEGER, VARCHAR, Column, Date, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID


@as_declarative()
class Base:
    id: UUID = Column(
        UUID(as_uuid=True), primary_key=True, server_default=text('uuid_generate_v4()'),
    )

    created_at = Column(DateTime(timezone=True), server_default=sql.func.now())
    created_by = Column(VARCHAR(255), nullable=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    updated_by = Column(VARCHAR(255), nullable=True)

    @declared_attr
    def __tablename__(cls):  # noqa 805
        return cls.__name__.lower()


class TariffOrderModel(Base):
    __tablename__ = 'order_tariffs'

    type = Column(VARCHAR(255), nullable=False)
    tariff_concat_code = Column(VARCHAR(255), nullable=False)

    def __repr__(self):
        return f'{self.type} - {self.tariff_concat_code}'


class OrderModel(Base):
    __tablename__ = 'order'

    order_form_number = Column(VARCHAR(255), nullable=False, comment='Номер бланка заказа')
    order_form_date = Column(Date(), nullable=True, comment='Дата бланка заказа')
    contract_number = Column(VARCHAR(255), nullable=False, comment='Номер договора')
    contract_date = Column(Date(), nullable=True, comment='Дата заключения договора')
    service = Column(VARCHAR(255), nullable=False, comment='Услуга')
    type_order_prod = Column(BOOLEAN, nullable=False, default=True, comment='')
    authorized_persons_of_the_contractor = Column(JSONB, comment='Уполномоченные лица исполнителя')
    authorized_persons_of_the_customer = Column(JSONB, comment='Уполномоченные лица заказчика')
    technical_parameters_of_the_services = Column(JSONB, comment='Технические параметры услуг')
    tariffs = Column(JSONB, comment='Тарифы БЗ')
    date_of_technological_readiness_of_services = Column(
        Date(), nullable=True,
        comment='Дата технологической готовности оказания услуги'
    )
    service_billing_start_date = Column(Date(), nullable=True, comment='')
    service_billing_stop_date = Column(Date(), nullable=True, comment='')
    initial_term_of_service_provision = Column(INTEGER(), nullable=False, comment='')
    service_source = Column(VARCHAR(255), nullable=False, comment='Где описана услуга')
    special_pricing_conditions_for_services = Column(Text(), comment='')
    signatories = Column(JSONB, comment='Подписанты')
    consumer_organization = Column(VARCHAR(255), nullable=False, comment='Организация заказчика')
    template_form = Column(VARCHAR(255), nullable=False, comment='')
    template_blank = Column(VARCHAR(255), nullable=False, comment='')
    active = Column(BOOLEAN, nullable=False, default=True, comment='')
    previous_order_for = Column(UUID(as_uuid=True), nullable=True, comment='')
    next_order_form = Column(UUID(as_uuid=True), nullable=True, comment='')

    def __repr__(self):
        return f'Сервис ({self.service}). Заказ {self.order_form_number}'