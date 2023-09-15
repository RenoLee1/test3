from django import forms
from django.forms import ModelForm
from django.http import HttpResponse
from django.shortcuts import render, redirect
from meal.utils.encrypt import md5
from django.core.exceptions import ValidationError
# import openai

from meal import models
from django.contrib.auth import logout


# Create your views here.

def home(request):
    return render(request, "home.html")


def logout_view(request):
    logout(request)
    return redirect("/")


class RegisterModelForm(ModelForm):
    confirm_password = forms.CharField(
        label="Confirm Password", widget=forms.PasswordInput(render_value=True))

    class Meta:
        model = models.UserInfo
        fields = ["user_name", "password", "confirm_password", "email"]
        widgets = {
            "password": forms.PasswordInput(render_value=True)
        }

    def clean_user_name(self):
        """确认用户名是否已被使用"""
        user_name = self.cleaned_data.get("user_name")
        print(f"clean_username is called with {user_name}")
        if models.UserInfo.objects.filter(user_name=user_name).exists():
            raise ValidationError("用户名已被使用")
        return user_name

    def clean_email(self):
        """确认邮箱是否已被使用"""
        email = self.cleaned_data.get("email")
        if models.UserInfo.objects.filter(email=email).exists():
            raise ValidationError("邮箱已被绑定")
        return email

    def clean_password(self):
        pwd = self.cleaned_data.get("password")
        return md5(pwd)

    def clean_confirm_password(self):
        pwd = self.cleaned_data.get("password")
        confirm = md5(self.cleaned_data.get("confirm_password"))
        if pwd != confirm:
            raise ValidationError("password not the same")
        return confirm

class LoginForm(forms.Form):
    user_name = forms.CharField(
        label='username',
        widget=forms.TextInput,
        required=True
    )
    password = forms.CharField(
        label='password',
        widget=forms.PasswordInput(render_value=True),
        required=True
    )

    def clean_password(self):
        pwd = self.cleaned_data.get("password")
        return md5(pwd)
def login(request):

    if request.method == 'GET':
        form = LoginForm()
        return render(request, 'login.html', {"form": form})

    # 获取提交的按键值
    # button_value = request.POST.get('button_value', '')

    # get
    if request.method == 'POST':
        if 'login' in request.POST:
            button_value = 'login'
        elif 'signup' in request.POST:
            button_value = 'signup'
        elif 'forgot_password' in request.POST:
            button_value = 'forgot_password'
        else:
            button_value = None

    if button_value == 'login':
        """点击登录"""

        form = LoginForm(data=request.POST)
        if form.is_valid():
            admin_object = models.UserInfo.objects.filter(
                **form.cleaned_data).first()

            if not admin_object:
                # 错误信息显示在密码下边
                form.add_error("password", "username or password get wrong")
                return render(request, 'login.html', {"form": form})

            return redirect('/login/')

    elif button_value == 'signup':
        """点击注册"""
        return redirect('/register/')

    elif button_value == 'forgot_password':
        """点击忘记密码"""
        return redirect('/forget_pwd/')

    return render(request, 'login.html', {"form": form})


class ForgetPwdModelForm(ModelForm):
    user_name = forms.CharField(
        label='username',
        widget=forms.TextInput,
        required=True
    )
    password = forms.CharField(
        label='password',
        widget=forms.PasswordInput(render_value=True),
        required=True
    )

    email = forms.CharField(
        label='email',
        widget=forms.TextInput,
        required=True
    )

    confirm_password = forms.CharField(
        label="Confirm Password", widget=forms.PasswordInput(render_value=True))

    class Meta:
        model = models.UserInfo
        fields = ["user_name", "password", "confirm_password", "email"]
        widgets = {
            "password": forms.PasswordInput(render_value=True)
        }

    def clean(self):
        cleaned_data = super().clean()

        user_name = cleaned_data.get("user_name")
        email = cleaned_data.get("email")
        new_password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if not new_password:
            self.add_error("password", "Password cannot be empty")

        if not confirm_password:
            self.add_error("confirm_password",
                           "Confirm password cannot be empty")

        # 在进行任何其他验证之前先进行这些检查。
        if not user_name or not email or not new_password or not confirm_password:
            return cleaned_data

        user_query = models.UserInfo.objects.filter(
            user_name=user_name, email=email)

        if not user_query.exists():
            raise ValidationError(
                "User does not exist")

        # 获取用户对象
        user = user_query.first()

        # 检查新密码是否与旧密码相同
        if user.password == md5(new_password):
            raise ValidationError(
                "The new password cannot be the same as the old password")

        if new_password and confirm_password:
            if new_password != confirm_password:
                raise ValidationError("Password not the same")

        return cleaned_data


def forget_pwd(request):
    '''忘记密码'''
    if request.method == 'GET':
        form = ForgetPwdModelForm()
        return render(request, 'forget_pwd.html', {"form": form})

    if request.method == 'POST':
        form = ForgetPwdModelForm(data=request.POST)
        if form.is_valid():
            # 如果表单有效，则获取用户数据
            user_name = form.cleaned_data.get("user_name")
            email = form.cleaned_data.get("email")
            password = md5(form.cleaned_data.get("password"))

            # 获取用户对象
            user = models.UserInfo.objects.get(
                user_name=user_name, email=email)
            # 更新用户的密码
            user.password = password  # 密码应该已经在表单验证中被加密
            user.save()

            return redirect('/login/')
    return render(request, 'forget_pwd.html', {"form": form})


def logout(request):
    return redirect('/login/')


class FitModelForm(ModelForm):
    class Meta:
        model = models.BodyInfo
        fields = ["height", "weight", "age", "gender", "user_id"]


def register(request):
    '''注册账户'''
    if request.method == 'GET':
        form = RegisterModelForm()
        return render(request, 'register.html', {"form": form})

    form = RegisterModelForm(data=request.POST)
    if form.is_valid():
        form.save()
        return redirect('/login/')

    return render(request, 'register.html', {"form": form})


def fit(request):
    if request.method == 'GET':
        form = FitModelForm()
        return render(request, 'register.html', {"form": form})

    form = FitModelForm(data=request.POST)
    if form.is_valid():
        form.save()
        return redirect('/login/')

    return render(request, 'register.html', {"form": form})

# def chat_box(request):
#     if request.method == "GET":
#         return render(request, 'test.html')
#
#     quest_str = request.POST.get('username')
#     openai.api_key="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"
#     model_engine = 'text-davinci-003'
#     prompt = "hello.how are you"
#
#     completion = openai.Completion.create(
#         engine=model_engine,
#         prompt=prompt,
#         max_tokens=20,
#         n=1,
#         stop=None,
#         temperature=0.5,
#     )
#
#     response = completion.choices[0].text
#     print(response)
#
#
#     return HttpResponse("success")
