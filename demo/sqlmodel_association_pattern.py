from typing import List, Optional

from sqlmodel import Field, Relationship, Session, SQLModel, create_engine, select


class HeroTeamLink(SQLModel, table=True):
    team_id: Optional[int] = Field(
        default=None, foreign_key="team.id", primary_key=True
    )
    hero_id: Optional[int] = Field(
        default=None, foreign_key="hero.id", primary_key=True
    )
    team_position_id: Optional[int] = Field(
        default=None, foreign_key="team_position.id", primary_key=True
    )


class Team_Position(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    team_position: str = Field(nullable=False)
    members: List["Hero"] = Relationship(
        back_populates="position", link_model=HeroTeamLink
    )


class Team(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    headquarters: str

    heroes: List["Hero"] = Relationship(back_populates="teams", link_model=HeroTeamLink)


class Hero(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    secret_name: str
    age: Optional[int] = Field(default=None, index=True)

    teams: List[Team] = Relationship(back_populates="heroes", link_model=HeroTeamLink)
    position: List[Team_Position] = Relationship(
        back_populates="members", link_model=HeroTeamLink
    )


sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

engine = create_engine(sqlite_url, echo=True)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def create_heroes():
    with Session(engine) as session:
        # a predefined lookup table for team positions
        team_positions_manager = Team_Position(team_position="Manager")
        team_position_member = Team_Position(team_position="Member")
        session.add(team_positions_manager)
        session.add(team_position_member)

        team_preventers = Team(name="Preventers", headquarters="Sharp Tower")
        team_z_force = Team(name="Z-Force", headquarters="Sister Margaret's Bar")
        session.add(team_preventers)
        session.add(team_z_force)

        hero_deadpond = Hero(
            name="Deadpond",
            secret_name="Dive Wilson",
            # teams=[team_z_force, team_preventers],
        )
        hero_rusty_man = Hero(
            name="Rusty-Man",
            secret_name="Tommy Sharp",
            age=48,
            # teams=[team_preventers],
        )
        hero_spider_boy = Hero(
            name="Spider-Boy",
            secret_name="Pedro Parqueador",
            # teams=[team_preventers]
        )
        session.add(hero_deadpond)
        session.add(hero_rusty_man)
        session.add(hero_spider_boy)
        session.flush()  # to populate primary keys

        # create relationships between heroes, teams and their positions
        hero_deadpond_manager_zforce = HeroTeamLink(
            team_id=team_z_force.id,
            hero_id=hero_deadpond.id,
            team_position_id=team_positions_manager.id,
        )
        hero_deadpond_member_preventers = HeroTeamLink(
            team_id=team_preventers.id,
            hero_id=hero_deadpond.id,
            team_position_id=team_position_member.id,
        )
        hero_rusty_member_preventers = HeroTeamLink(
            team_id=team_preventers.id,
            hero_id=hero_rusty_man.id,
            team_position_id=team_position_member.id,
        )
        session.add(hero_deadpond_manager_zforce)
        session.add(hero_deadpond_member_preventers)
        session.add(hero_rusty_member_preventers)

        # etc....

        session.commit()

        session.refresh(hero_deadpond)
        session.refresh(hero_rusty_man)
        session.refresh(hero_spider_boy)

        print("Deadpond:", hero_deadpond)
        print("Deadpond teams:", hero_deadpond.teams)
        print("Deadpond Position:", hero_deadpond.position)
        print("Rusty-Man:", hero_rusty_man)
        print("Rusty-Man Teams:", hero_rusty_man.teams)
        print("Rusty-Man Positions:", hero_rusty_man.position)

        print("Spider-Boy:", hero_spider_boy)
        print("Spider-Boy Teams:", hero_spider_boy.teams)

        # --- example of what would be nice, but doesn't work
        # hero_borat = Hero(
        #     name="Sasha Baron Cohen",
        #     secret_name="Borat Sagdiyev",
        #     teams=[team_preventers],
        #     position=[team_positions_manager],
        # )
        # print("adding borat...")
        # session.add(hero_borat)
        # session.flush()
        # print("added borat...")


def update_heroes():
    with Session(engine) as session:
        hero_spider_boy = session.exec(
            select(Hero).where(Hero.name == "Spider-Boy")
        ).one()
        team_z_force = session.exec(select(Team).where(Team.name == "Z-Force")).one()

        team_z_force.heroes.append(hero_spider_boy)
        session.add(team_z_force)
        session.commit()

        print("Updated Spider-Boy's Teams:", hero_spider_boy.teams)
        print("Z-Force heroes:", team_z_force.heroes)

        hero_spider_boy.teams.remove(team_z_force)
        session.add(team_z_force)
        session.commit()

        print("Reverted Z-Force's heroes:", team_z_force.heroes)
        print("Reverted Spider-Boy's teams:", hero_spider_boy.teams)


def main():
    create_db_and_tables()
    create_heroes()
    # update_heroes()


if __name__ == "__main__":
    main()
