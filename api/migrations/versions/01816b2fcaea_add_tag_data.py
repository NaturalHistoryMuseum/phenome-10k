"""
Add tag data.

Revision ID: 01816b2fcaea
Revises: 77f6b43f2bfa
Create Date: 2024-03-12 16:10:30.144815
"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy import orm
from sqlalchemy.dialects.mysql import insert
from sqlalchemy.ext.declarative import declarative_base

# revision identifiers, used by Alembic.
revision = '01816b2fcaea'
down_revision = '77f6b43f2bfa'
branch_labels = None
depends_on = None

data = [
    (17, 'geologic_age', 'Extant', 'extant', None),
    (18, 'geologic_age', 'Cenozoic', 'cenozoic', None),
    (19, 'geologic_age', 'Paleocene', 'cenozoic/paleocene', 18),
    (20, 'geologic_age', 'Oligocene', 'cenozoic/oligocene', 18),
    (21, 'geologic_age', 'Miocene', 'cenozoic/miocene', 18),
    (22, 'geologic_age', 'Pliocene', 'cenozoic/pliocene', 18),
    (23, 'geologic_age', 'Pleistocene', 'cenozoic/leistocene', 18),
    (24, 'geologic_age', 'Holocene', 'cenozoic/holocene', 18),
    (25, 'geologic_age', 'Mesozoic', 'mesozoic', None),
    (26, 'geologic_age', 'Triassic', 'mesozoic/triassic', 25),
    (27, 'geologic_age', 'Jurassic', 'mesozoic/jurassic', 25),
    (28, 'geologic_age', 'Cretaceous', 'mesozoic/cretaceous', 25),
    (30, 'elements', 'Skeleton', 'skeleton', None),
    (31, 'elements', 'Cranium', 'skeleton/cranium', 30),
    (32, 'elements', 'Mandible', 'skeleton/mandible', 30),
    (33, 'elements', 'Teeth', 'skeleton/teeth', 30),
    (34, 'elements', 'Postcranium', 'skeleton/postcranium', 30),
    (35, 'elements', 'Soft Tissue', 'skeleton/soft_tissue', 30),
    (36, 'elements', 'Stem', 'stem', None),
    (37, 'elements', 'Seed', 'seed', None),
    (38, 'elements', 'Leaf', 'leaf', None),
    (39, 'elements', 'Flower', 'flower', None),
    (40, 'elements', 'Root', 'root', None),
    (41, 'elements', 'Wood', 'wood', None),
    (43, 'ontogenic_age', 'Adult', 'adult', None),
    (44, 'ontogenic_age', 'Subadult', 'subadult', None),
    (45, 'ontogenic_age', 'Juvenile', 'juvenile', None),
    (46, 'ontogenic_age', 'Infant', 'infant', None),
    (47, 'ontogenic_age', 'Larva', 'larva', None),
    (48, 'ontogenic_age', 'Embryo', 'embryo', None),
    (82, 'geologic_age', 'Eocene', 'cenozoic/eocene', 18),
    (83, 'geologic_age', 'Paleozoic', 'paleozoic', None),
    (84, 'geologic_age', 'Cambrian', 'paleozoic/cambrian', 83),
    (85, 'geologic_age', 'Ordovician', 'paleozoic/ordovician', 83),
    (86, 'geologic_age', 'Silurian', 'paleozoic/silurian', 83),
    (87, 'geologic_age', 'Devonian', 'paleozoic/devonian', 83),
    (88, 'geologic_age', 'Carboniferous', 'paleozoic/carboniferous', 83),
    (89, 'geologic_age', 'Permian', 'paleozoic/permian', 83),
    (90, 'geologic_age', 'Precambrian', 'precambrian', None),
]

Base = declarative_base()


class Tag(Base):
    __tablename__ = 'tag'
    id = sa.Column(sa.Integer, primary_key=True)
    category = sa.Column(sa.String(250), nullable=False)
    name = sa.Column(sa.String(250), nullable=False)
    taxonomy = sa.Column(sa.String(250), unique=True)
    parent_id = sa.Column(sa.Integer, sa.ForeignKey('tag.id'))


def upgrade():
    bind = op.get_bind()
    session = orm.Session(bind=bind)
    for row in data:
        insrt = insert(Tag).values(
            id=row[0], category=row[1], name=row[2], taxonomy=row[3], parent_id=row[4]
        )
        upsrt = insrt.on_duplicate_key_update(
            category=row[1], name=row[2], taxonomy=row[3], parent_id=row[4]
        )
        session.execute(upsrt)


def downgrade():
    bind = op.get_bind()
    session = orm.Session(bind=bind)
    for row in [r for r in data if r[4] is not None]:
        # delete rows with parents first
        dlt = sa.delete(Tag).where(Tag.id == row[0])
        session.execute(dlt)
    for row in [r for r in data if r[4] is None]:
        # now delete the parents
        dlt = sa.delete(Tag).where(Tag.id == row[0])
        session.execute(dlt)
