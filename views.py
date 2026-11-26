from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Profile, Post, Comment


def seed_demo_data():
    if User.objects.exists():
        return

    u1 = User.objects.create_user(
        username="madiha_dev",
        email="madiha@vibesocial.dev",
        password="password123",
        first_name="Madiha Eman",
    )
    p1_profile, _ = Profile.objects.get_or_create(user=u1)
    p1_profile.bio = "Software Engineering Student | Full-Stack & UI/UX Enthusiast 💜"
    p1_profile.badge = "Pro Builder"
    p1_profile.save()

    u2 = User.objects.create_user(
        username="alex_ui",
        email="alex@vibesocial.dev",
        password="password123",
        first_name="Alex Rivera",
    )
    p2_profile, _ = Profile.objects.get_or_create(user=u2)
    p2_profile.bio = "Product Designer crafting rich purple & neon dark-mode UIs."
    p2_profile.badge = "UI Designer"
    p2_profile.save()

    u3 = User.objects.create_user(
        username="sara_codes",
        email="sara@vibesocial.dev",
        password="password123",
        first_name="Sara Khan",
    )
    p3_profile, _ = Profile.objects.get_or_create(user=u3)
    p3_profile.bio = "Django & Cloud developer sharing clean full-stack workflows."
    p3_profile.badge = "Tech Lead"
    p3_profile.save()

    p1_profile.following.add(p2_profile, p3_profile)
    p2_profile.following.add(p1_profile)

    post1 = Post.objects.create(
        author=u1,
        content="Just built VibeSocial with Django & SQLite in a Rich Purple + Neon Pink theme! Profiles, posts, likes, comments & follow system all wired up 🚀💜",
        image_url="https://images.unsplash.com/photo-1555066931-4365d14bab8c?auto=format&fit=crop&w=900&q=80",
        tag="WebDev",
    )
    post2 = Post.objects.create(
        author=u2,
        content="Neon magenta + deep violet gradients over dark glass cards give social feeds instant energy. How do you style your cards?",
        image_url="https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&w=900&q=80",
        tag="UIUX",
    )
    post3 = Post.objects.create(
        author=u3,
        content="Tip for internship tasks: test auth, CRUD, and relationships early so frontend templates stay super clean.",
        tag="CareerTips",
    )

    post1.likes.add(u2, u3)
    post2.likes.add(u1)

    Comment.objects.create(post=post1, author=u2, text="Love the rich purple + neon pink vibe! 🔥")
    Comment.objects.create(post=post3, author=u1, text="Super helpful tip, thanks Sara!")


def feed_view(request):
    try:
        seed_demo_data()
    except Exception:
        pass

    q = request.GET.get("q", "").strip()
    tag = request.GET.get("tag", "All").strip() or "All"

    posts = Post.objects.select_related("author", "author__profile").prefetch_related("comments__author", "likes").order_by("-created_at")
    if tag != "All":
        posts = posts.filter(tag=tag)
    if q:
        posts = posts.filter(Q(content__icontains=q) | Q(author__username__icontains=q))

    suggested_users = User.objects.select_related("profile").exclude(id=request.user.id if request.user.is_authenticated else -1)[:5]
    tags = ["All", "WebDev", "UIUX", "CareerTips", "General"]

    if request.user.is_authenticated:
        Profile.objects.get_or_create(user=request.user)

    return render(request, "feed.html", {
        "posts": posts,
        "suggested_users": suggested_users,
        "tags": tags,
        "selected_tag": tag,
        "search_query": q,
    })


@login_required
def create_post_view(request):
    if request.method == "POST":
        content = request.POST.get("content", "").strip()
        image_url = request.POST.get("image_url", "").strip()
        tag = request.POST.get("tag", "General").strip() or "General"

        if not content:
            messages.error(request, "Please write something before posting.")
        else:
            Post.objects.create(
                author=request.user,
                content=content,
                image_url=image_url,
                tag=tag,
            )
            messages.success(request, "Your post is live!")
    return redirect("feed")


@login_required
def toggle_like_view(request, post_id):
    if request.method == "POST":
        post = get_object_or_404(Post, id=post_id)
        if request.user in post.likes.all():
            post.likes.remove(request.user)
        else:
            post.likes.add(request.user)
    return redirect(request.META.get("HTTP_REFERER", "feed"))


@login_required
def add_comment_view(request, post_id):
    if request.method == "POST":
        post = get_object_or_404(Post, id=post_id)
        text = request.POST.get("text", "").strip()
        if text:
            Comment.objects.create(post=post, author=request.user, text=text)
            messages.success(request, "Comment posted!")
        else:
            messages.error(request, "Comment cannot be empty.")
    return redirect(request.META.get("HTTP_REFERER", "feed"))


@login_required
def delete_post_view(request, post_id):
    if request.method == "POST":
        post = get_object_or_404(Post, id=post_id, author=request.user)
        post.delete()
        messages.success(request, "Post deleted.")
    return redirect(request.META.get("HTTP_REFERER", "feed"))


def profile_view(request, username):
    profile_user = get_object_or_404(User, username=username)
    user_profile, _ = Profile.objects.get_or_create(user=profile_user)
    posts = Post.objects.filter(author=profile_user).prefetch_related("comments__author", "likes").order_by("-created_at")

    is_following = False
    if request.user.is_authenticated and request.user != profile_user:
        my_profile, _ = Profile.objects.get_or_create(user=request.user)
        is_following = user_profile in my_profile.following.all()

    return render(request, "profile.html", {
        "profile_user": profile_user,
        "user_profile": user_profile,
        "posts": posts,
        "is_following": is_following,
    })


@login_required
def update_profile_view(request):
    if request.method == "POST":
        prof, _ = Profile.objects.get_or_create(user=request.user)
        bio = request.POST.get("bio", "").strip()
        badge = request.POST.get("badge", "").strip()
        if bio:
            prof.bio = bio
        if badge:
            prof.badge = badge
        prof.save()
        messages.success(request, "Profile updated!")
    return redirect("profile", username=request.user.username)


@login_required
def toggle_follow_view(request, username):
    if request.method == "POST":
        target_user = get_object_or_404(User, username=username)
        if target_user != request.user:
            target_profile, _ = Profile.objects.get_or_create(user=target_user)
            my_profile, _ = Profile.objects.get_or_create(user=request.user)
            if target_profile in my_profile.following.all():
                my_profile.following.remove(target_profile)
                messages.success(request, f"Unfollowed @{target_user.username}.")
            else:
                my_profile.following.add(target_profile)
                messages.success(request, f"Following @{target_user.username}!")
    return redirect(request.META.get("HTTP_REFERER", "feed"))


def register_view(request):
    if request.method == "POST":
        full_name = request.POST.get("full_name", "").strip()
        username = request.POST.get("username", "").strip().lower().replace(" ", "_")
        email = request.POST.get("email", "").strip().lower()
        password = request.POST.get("password", "")

        if not full_name or not username or not email or len(password) < 6:
            messages.error(request, "Please fill all fields (password must be at least 6 characters).")
            return redirect("register")

        if User.objects.filter(Q(username=username) | Q(email=email)).exists():
            messages.error(request, "Username or email already exists.")
            return redirect("register")

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=full_name,
        )
        Profile.objects.get_or_create(user=user)
        login(request, user)
        messages.success(request, f"Welcome to VibeSocial, {full_name}!")
        return redirect("feed")

    return render(request, "register.html")


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip().lower()
        password = request.POST.get("password", "")
        user = authenticate(request, username=username, password=password)
        if user:
            Profile.objects.get_or_create(user=user)
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect("feed")
        messages.error(request, "Invalid username or password.")
    return render(request, "login.html")


def logout_view(request):
    logout(request)
    messages.success(request, "Logged out.")
    return redirect("feed")