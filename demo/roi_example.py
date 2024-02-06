import os
from typing import List, Optional

from sqlmodel import Field, Relationship, Session, SQLModel, create_engine, select

# Example code on some ideas around how to implement the junction table
# idea that maintains relationship to multiple tables


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

    is_training: bool = False

    hero: "Hero" = Relationship(back_populates="team_links")
    team: "Team" = Relationship(back_populates="hero_links")
    position: "Team_Position" = Relationship(back_populates="members")


class Team_Position(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    team_position: str = Field(nullable=False)
    members: List[HeroTeamLink] = Relationship(back_populates="position")

    position_links: List[HeroTeamLink] = Relationship(back_populates="position")


class Team(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    headquarters: str

    hero_links: List[HeroTeamLink] = Relationship(back_populates="team")


class Hero(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    secret_name: str
    age: Optional[int] = Field(default=None, index=True)

    team_links: List[HeroTeamLink] = Relationship(back_populates="hero")


sqlite_file_name = "roi.db"
if os.path.exists(sqlite_file_name):
    os.remove(sqlite_file_name)
sqlite_url = f"sqlite:///{sqlite_file_name}"

engine = create_engine(sqlite_url, echo=True)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def create_heroes():
    with Session(engine) as session:
        # Define and enter positions
        team_positions_manager = Team_Position(team_position="Manager")
        team_position_member = Team_Position(team_position="Member")
        session.add(team_positions_manager)
        session.add(team_position_member)

        # define and enter teams
        team_preventers = Team(name="Preventers", headquarters="Sharp Tower")
        team_z_force = Team(name="Z-Force", headquarters="Sister Margaret’s Bar")

        # define and enter heros
        hero_deadpond = Hero(
            name="Deadpond",
            secret_name="Dive Wilson",
        )
        hero_rusty_man = Hero(
            name="Rusty-Man",
            secret_name="Tommy Sharp",
            age=48,
        )
        hero_spider_boy = Hero(
            name="Spider-Boy",
            secret_name="Pedro Parqueador",
        )

        # add heros to teams / position combinations
        deadpond_team_z_link = HeroTeamLink(
            team=team_z_force, hero=hero_deadpond, position=team_positions_manager
        )
        deadpond_preventers_link = HeroTeamLink(
            team=team_preventers,
            hero=hero_deadpond,
            is_training=True,
            position=team_position_member,
        )
        spider_boy_preventers_link = HeroTeamLink(
            team=team_preventers,
            hero=hero_spider_boy,
            is_training=True,
            position=team_position_member,
        )
        rusty_man_preventers_link = HeroTeamLink(
            team=team_preventers, hero=hero_rusty_man, position=team_position_member
        )

        session.add(deadpond_team_z_link)
        session.add(deadpond_preventers_link)
        session.add(spider_boy_preventers_link)
        session.add(rusty_man_preventers_link)
        session.commit()

        current_hero = hero_deadpond

        session.refresh(current_hero)

        print(f"THE GUY: {current_hero} {current_hero.team_links}")
        for hero_team_link in current_hero.team_links:
            print(f"Link Object: {hero_team_link}")
            print(f"Link Object team: {hero_team_link.team} ")
            print(f"Link Object hero: {hero_team_link.hero}")
            print(f"Link Object position: {hero_team_link.position}")

        # print(f"Link Object: {spider_boy_preventers_link}")
        # print(f"Link Object team: {spider_boy_preventers_link.team} ")
        # print(f"Link Object hero: {spider_boy_preventers_link.hero}")
        # print(f"Link Object position: {spider_boy_preventers_link.position}")

        # for link in team_z_force.hero_links:
        #     print("Z-Force hero:", link.hero, "is training:", link.is_training)

        # for link in team_preventers.hero_links:
        #     print("Preventers hero:", link.hero, "is training:", link.is_training)


def update_heroes():
    with Session(engine) as session:
        hero_spider_boy = session.exec(
            select(Hero).where(Hero.name == "Spider-Boy")
        ).one()
        team_z_force = session.exec(select(Team).where(Team.name == "Z-Force")).one()

        spider_boy_z_force_link = HeroTeamLink(
            team=team_z_force, hero=hero_spider_boy, is_training=True
        )
        team_z_force.hero_links.append(spider_boy_z_force_link)
        session.add(team_z_force)
        session.commit()

        print("Updated Spider-Boy's Teams:", hero_spider_boy.team_links)
        print("Z-Force heroes:", team_z_force.hero_links)

        for link in hero_spider_boy.team_links:
            if link.team.name == "Preventers":
                link.is_training = False

        session.add(hero_spider_boy)
        session.commit()

        for link in hero_spider_boy.team_links:
            print("Spider-Boy team:", link.team, "is training:", link.is_training)


def main():
    create_db_and_tables()
    create_heroes()
    # update_heroes()


if __name__ == "__main__":
    main()
