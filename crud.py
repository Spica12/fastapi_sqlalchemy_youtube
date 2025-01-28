import asyncio

from sqlalchemy import Result, select, ScalarResult
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from core.models import (
    db_helper,
    User,
    Profile,
    Post,
    Order,
    Product,
    OrderProductAssociation,
)


async def create_user(session: AsyncSession, username: str) -> User:
    user = User(username=username)
    session.add(user)
    await session.commit()
    print(user)
    return user


async def get_user_by_username(session: AsyncSession, username: str) -> User | None:
    stmt = select(User).where(User.username == username)
    result: Result = await session.execute(stmt)
    user: User | None = result.scalar_one_or_none()
    print(f"Found user: {username}, {user}")
    return user


async def create_user_profile(
    session: AsyncSession,
    user_id: int,
    first_name: str | None = None,
    last_name: str | None = None,
    bio: str | None = None,
) -> Profile:
    profile = Profile(
        user_id=user_id,
        first_name=first_name,
        last_name=last_name,
        bio=bio,
    )
    session.add(profile)
    await session.commit()
    print(profile)
    return profile


async def show_users_with_profiles(
    session: AsyncSession,
) -> list[User]:
    stmt = select(User).options(joinedload(User.profile)).order_by(User.id)
    result: Result = await session.execute(stmt)
    users: ScalarResult = result.scalars()
    for user in users:
        user: User
        print(user, user.profile.first_name)


async def create_posts(
    session: AsyncSession, user_id: int, *posts_titles: str
) -> list[Post]:
    posts = [Post(title=title, user_id=user_id) for title in posts_titles]
    session.add_all(posts)
    await session.commit()
    print(posts)
    return posts


async def get_users_with_posts(session: AsyncSession):
    # stmt = select(User).options(joinedload(User.posts)).order_by(User.id)
    # users: ScalarResult = await session.scalars(stmt)
    stmt = (
        select(User)
        .options(
            # joinedload(User.posts)
            selectinload(User.posts)
        )
        .order_by(User.id)
    )
    result: Result = await session.execute(stmt)
    users = result.unique().scalars()
    for user in users:
        user: User
        print("**" * 10)
        print(user)
        for post in user.posts:
            post: Post
            print("-", post)


async def get_posts_with_with_autors(session: AsyncSession):
    # stmt = select(User).options(joinedload(User.posts)).order_by(User.id)
    # users: ScalarResult = await session.scalars(stmt)
    stmt = select(Post).options(joinedload(Post.user)).order_by(Post.id)
    posts: ScalarResult = await session.scalars(stmt)
    for post in posts:
        post: Post
        print("-", post)
        print("author", post.user)


async def get_users_with_posts_and_profiles(session: AsyncSession):
    stmt = (
        select(User)
        .options(joinedload(User.profile), selectinload(User.posts))
        .order_by(User.id)
    )
    users: ScalarResult = await session.scalars(stmt)
    for user in users:
        user: User
        print("**" * 10)
        print(user, user.profile and user.profile.first_name)
        for post in user.posts:
            post: Post
            print("-", post)


async def get_profiles_with_users_and_users_with_posts(session: AsyncSession):
    stmt = (
        select(Profile)
        .options(joinedload(Profile.user).selectinload(User.posts))
        .order_by(Profile.id)
    )

    # stmt = (
    #     select(Profile)
    #     .join(Profile.user)
    #     .options(
    #         joinedload(Profile.user).selectinload(User.posts)
    #     )
    #     .where(User.username == 'John')
    #     .order_by(Profile.id)
    # )

    profiles: ScalarResult = await session.scalars(stmt)

    for profile in profiles:
        profile: Profile
        print("*" * 10)
        print(profile.first_name, profile.user)
        print(profile.user.posts)


async def main_relations(session: AsyncSession):
    # await create_user(session, username="John")
    # await create_user(session, username="Sam")
    # await create_user(session, username="Ben")

    user_sam = await get_user_by_username(session, "Sam")
    # await get_user_by_username(session, "Tom")
    await get_user_by_username(session, "Ben")
    user_john = await get_user_by_username(session, "John")

    # await create_user_profile(session=session, user_id=user_sam.id, first_name="SaM")
    # await create_user_profile(session=session, user_id=user_john.id, first_name="JohN", last_name="White")
    # await show_users_with_profiles(session)

    # await create_posts(session, user_sam.id, "SQLA 2.0", "SQLA Joins")
    # await create_posts(session, user_john.id, "FASTAPI intro", "FASTAPI Advanced")

    await get_users_with_posts(session)

    print("--------------------")
    await get_posts_with_with_autors(session)

    await get_users_with_posts_and_profiles(session)

    print("-+-")
    await get_profiles_with_users_and_users_with_posts(session)


async def create_order(session: AsyncSession, promocode: str | None = None) -> Order:
    order = Order(promocode=promocode)
    session.add(order)
    await session.commit()
    return order


async def create_product(
    session: AsyncSession, name: str, description: str, price: int
) -> Product:
    product = Product(
        name=name,
        description=description,
        price=price,
    )
    session.add(product)
    await session.commit()
    return product


async def create_orders_and_products(session: AsyncSession) -> None:
    order1 = await create_order(session)
    order2 = await create_order(session, "SQLALCHEMY")

    mouse = await create_product(
        session,
        "mouse",
        "Great gaming mouse",
        price=123,
    )
    keyboard = await create_product(
        session,
        "keyboard",
        "Great gaming keyboard",
        price=235,
    )
    display = await create_product(
        session,
        "display",
        "Great office display",
        price=299,
    )

    order1 = await session.scalar(
        select(Order)
        .where(Order.id == order1.id)
        .options(
            selectinload(Order.products),
        ),
    )

    order2 = await session.scalar(
        select(Order)
        .where(Order.id == order2.id)
        .options(
            selectinload(Order.products),
        ),
    )

    order1.products.append(mouse)
    order1.products.append(keyboard)
    order2.products = [keyboard, display]

    await session.commit()


async def get_orders_with_products(session: AsyncSession) -> list[Order]:
    stmt = (
        select(Order)
        .options(
            selectinload(Order.products),
        )
        .order_by(Order.id)
    )
    orders: ScalarResult = await session.scalars(stmt)

    return list(orders)


async def get_orders_with_products_associations(session: AsyncSession) -> list[Order]:
    stmt = (
        select(Order)
        .options(
            selectinload(Order.products_details).joinedload(
                OrderProductAssociation.product
            ),
        )
        .order_by(Order.id)
    )
    orders: ScalarResult = await session.scalars(stmt)

    return list(orders)


async def demo_get_orders_with_products_through_secondary(session: AsyncSession):
    orders: list[Order] = await get_orders_with_products(session)
    for order in orders:
        order: Order
        print(order.id, order.promocode, order.created_at, "products:")
        for product in order.products:
            product: Product
            print("-", product.id, product.name, product.price)


async def demo_get_orders_with_products_with_associations(session: AsyncSession):
    orders: list[Order] = await get_orders_with_products_associations(session)
    for order in orders:
        order: Order
        print(order.id, order.promocode, order.created_at, "products:")
        for order_product_details in order.products_details:
            order_product_details: OrderProductAssociation
            print(
                "-",
                order_product_details.product.id,
                order_product_details.product.name,
                order_product_details.product.price,
                "qty:",
                order_product_details.count,
            )

async def create_gift_products_for_existing_orders(session: AsyncSession):
    orders: list[Order] = await get_orders_with_products_associations(session)

    gift_product = await create_product(session, "Gift", "Gift product", price=0)
    for order in orders:
        order: Order
        order.products_details.append(
            OrderProductAssociation(
                product=gift_product,
                count=1,
                unit_price=0,
            )
        )

    await session.commit()


async def demo_m2m(session: AsyncSession):
    # await create_orders_and_products(session)

    # await demo_get_orders_with_products_through_secondary(session)
    await demo_get_orders_with_products_with_associations(session)

    # await create_gift_products_for_existing_orders(session)


async def main():
    async with db_helper.session_factory() as session:
        # Lesson 3
        # await main_relations(session)

        # Lesson 4
        await demo_m2m(session)


if __name__ == "__main__":
    asyncio.run(main())
