"use strict";var rtl_flag=!1,dark_flag=!1;function layout_change_default(){let t=window.matchMedia("(prefers-color-scheme: dark)").matches?"dark":"light";layout_change(t);var e=document.querySelector('.theme-layout .btn[data-value="default"]');e&&e.classList.add("active"),window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change",e=>{layout_change(t=e.matches?"dark":"light")})}document.addEventListener("DOMContentLoaded",function(){var e;"undefined"!=typeof Storage?(e=localStorage.getItem("theme"))&&layout_change(e):console.warn("Web Storage API is not supported in this browser.")});for(var layout_btn=document.querySelectorAll(".theme-layout .btn"),t=0;t<layout_btn.length;t++)layout_btn[t]&&layout_btn[t].addEventListener("click",function(e){e.stopPropagation();e=e.target;"true"==(e="SPAN"==(e="SPAN"==e.tagName?e.parentNode:e).tagName?e.parentNode:e).getAttribute("data-value")?localStorage.setItem("theme","light"):localStorage.setItem("theme","dark")});function layout_theme_contrast_change(e){var t=document.getElementsByTagName("body")[0],a=document.querySelector(".theme-contrast .btn.active"),t=(t.setAttribute("data-pc-theme_contrast",e),a&&a.classList.remove("active"),document.querySelector(`.theme-contrast .btn[data-value='${e}']`));t&&t.classList.add("active")}function layout_caption_change(e){"true"==e?(document.getElementsByTagName("body")[0].setAttribute("data-pc-sidebar-caption","true"),document.querySelector(".theme-nav-caption .btn.active")&&(document.querySelector(".theme-nav-caption .btn.active").classList.remove("active"),document.querySelector(".theme-nav-caption .btn[data-value='true']").classList.add("active"))):(document.getElementsByTagName("body")[0].setAttribute("data-pc-sidebar-caption","false"),document.querySelector(".theme-nav-caption .btn.active")&&(document.querySelector(".theme-nav-caption .btn.active").classList.remove("active"),document.querySelector(".theme-nav-caption .btn[data-value='false']").classList.add("active")))}function preset_change(e){document.getElementsByTagName("body")[0].setAttribute("data-pc-preset",e),document.querySelector(".pct-offcanvas")&&(document.querySelector(".preset-color > a.active").classList.remove("active"),document.querySelector(".preset-color > a[data-value='"+e+"']").classList.add("active"))}function layout_rtl_change(e){var t=document.getElementsByTagName("body")[0],a=document.getElementsByTagName("html")[0],o=document.querySelector(".theme-direction .btn.active");"true"===e?(rtl_flag=!0,t.setAttribute("data-pc-direction","rtl"),a.setAttribute("dir","rtl"),a.setAttribute("lang","ar"),o&&(o.classList.remove("active"),document.querySelector(".theme-direction .btn[data-value='true']").classList.add("acxtive"))):(rtl_flag=!1,t.setAttribute("data-pc-direction","ltr"),a.removeAttribute("dir"),a.removeAttribute("lang"),o&&(o.classList.remove("active"),document.querySelector(".theme-direction .btn[data-value='false']").classList.add("active")))}function layout_change(e){document.getElementsByTagName("body")[0].setAttribute("data-pc-theme",e);var t=document.querySelector('.theme-layout .btn[data-value="default"]');t&&t.classList.remove("active"),"dark"===e?(dark_flag=!0,updateLogo(".pc-sidebar .m-header .logo-lg","../assets/images/logo-white.svg"),updateLogo(".navbar-brand .logo-lg","../assets/images/logo-white.svg"),updateLogo(".auth-main.v1 .auth-sidefooter img","../assets/images/logo-white.svg"),updateLogo(".footer-top .footer-logo","../assets/images/logo-white.svg"),updateActiveButton('.theme-layout .btn[data-value="false"]')):(dark_flag=!1,updateLogo(".pc-sidebar .m-header .logo-lg","../assets/images/logo-dark.svg"),updateLogo(".navbar-brand .logo-lg","../assets/images/logo-dark.svg"),updateLogo(".auth-main.v1 .auth-sidefooter img","../assets/images/logo-dark.svg"),updateLogo(".footer-top .footer-logo","../assets/images/logo-dark.svg"),updateActiveButton('.theme-layout .btn[data-value="true"]'))}function updateLogo(e,t){e=document.querySelector(e);e&&e.setAttribute("src",t)}function updateActiveButton(e){var t=document.querySelector(".theme-layout .btn.active"),t=(t&&t.classList.remove("active"),document.querySelector(e));t&&t.classList.add("active")}function change_box_container(e){var t,a,o=document.querySelector(".pc-content"),c=document.querySelector(".footer-wrapper");o&&c&&("true"===e?(o.classList.add("container"),c.classList.add("container"),c.classList.remove("container-fluid"),(t=document.querySelector(".theme-container .btn.active"))&&t.classList.remove("active"),(a=document.querySelector('.theme-container .btn[data-value="true"]'))&&a.classList.add("active")):(o.classList.remove("container"),c.classList.remove("container"),c.classList.add("container-fluid"),(t=document.querySelector(".theme-container .btn.active"))&&t.classList.remove("active"),(a=document.querySelector('.theme-container .btn[data-value="false"]'))&&a.classList.add("active")))}document.addEventListener("DOMContentLoaded",function(){if(document.querySelectorAll(".preset-color"))for(var e=document.querySelectorAll(".preset-color > a"),t=0;t<e.length;t++)e[t].addEventListener("click",function(e){e=e.target;preset_change((e="SPAN"==e.tagName?e.parentNode:e).getAttribute("data-value"))});document.querySelector(".pct-body")&&new SimpleBar(document.querySelector(".pct-body"));var a=document.querySelector("#layoutreset");a&&a.addEventListener("click",function(e){localStorage.clear(),location.reload(),localStorage.setItem("layout","vertical")})});