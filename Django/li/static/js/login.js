$(function () {
    //猫头鹰的变化
    $('#password').focus(function () {
        // 密码框获得焦点，追加样式.password
        $('#owl').addClass('password');
    }).blur(function () {
        // 密码框失去焦点，移除样式.password
        $('#owl').removeClass('password');
    })
    // $("#login").click(function () {
    //     window.location.href = "http://127.0.0.1:5000/index"
    // })
});
