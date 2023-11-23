import { LayoutNavbarButton } from "./button.js"; export { LayoutNavbarButton };
import { html, nothing } from "../../utility/lit-core.min.js";
import { CustomElement } from "../../utility/utility.js";

// name: 服务原名
// page: 导航路径
// icon: 项目图标
// : 显示别名 (可选)
const navbar_list = [
  {
    name: "我的媒体库",
    page: "index",
    icon: html`
      <svg xmlns="http://www.w3.org/2000/svg" class="icon icon-tabler icon-tabler-home" width="24" height="24" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" fill="none" stroke-linecap="round" stroke-linejoin="round"><path stroke="none" d="M0 0h24v24H0z" fill="none"></path><polyline points="5 12 3 12 12 3 21 12 19 12"></polyline><path d="M5 12v7a2 2 0 0 0 2 2h10a2 2 0 0 0 2 -2v-7"></path><path d="M9 21v-6a2 2 0 0 1 2 -2h2a2 2 0 0 1 2 2v6"></path></svg>
    `,
  },
  {
    name: "媒体整理",
    list: [
      {
        name: "文件管理",
        page: "mediafile",
        icon: html`
          <!-- https://tabler-icons.io/static/tabler-icons/icons-png/file-pencil.png -->
          <svg xmlns="http://www.w3.org/2000/svg" class="icon icon-tabler icon-tabler-file-pencil" width="24" height="24" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" fill="none" stroke-linecap="round" stroke-linejoin="round">
            <path stroke="none" d="M0 0h24v24H0z" fill="none"></path>
            <path d="M14 3v4a1 1 0 0 0 1 1h4"></path>
            <path d="M17 21h-10a2 2 0 0 1 -2 -2v-14a2 2 0 0 1 2 -2h7l5 5v11a2 2 0 0 1 -2 2z"></path>
            <path d="M10 18l5 -5a1.414 1.414 0 0 0 -2 -2l-5 5v2h2z"></path>
          </svg>
        `,
      },
      {
        name: "手动识别",
        page: "unidentification",
        icon: html`
          <!-- https://tabler-icons.io/static/tabler-icons/icons-png/accessible.png -->
          <svg xmlns="http://www.w3.org/2000/svg" class="icon icon-tabler icon-tabler-accessible" width="24" height="24" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" fill="none" stroke-linecap="round" stroke-linejoin="round">
            <path stroke="none" d="M0 0h24v24H0z" fill="none"></path>
            <path d="M12 12m-9 0a9 9 0 1 0 18 0a9 9 0 1 0 -18 0"></path>
            <path d="M10 16.5l2 -3l2 3m-2 -3v-2l3 -1m-6 0l3 1"></path>
            <circle cx="12" cy="7.5" r=".5" fill="currentColor"></circle>
          </svg>
        `,
      },
      {
        name: "历史记录",
        page: "history",
        icon: html`
          <!-- https://tabler-icons.io/static/tabler-icons/icons-png/history.png -->
          <svg xmlns="http://www.w3.org/2000/svg" class="icon icon-tabler icon-tabler-history" width="24" height="24" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" fill="none" stroke-linecap="round" stroke-linejoin="round">
            <path stroke="none" d="M0 0h24v24H0z" fill="none"></path>
            <path d="M12 8l0 4l2 2"></path>
            <path d="M3.05 11a9 9 0 1 1 .5 4m-.5 5v-5h5"></path>
          </svg>
        `,
      },
      {
        name: "TMDB缓存",
        page: "tmdbcache",
        icon: html`
          <!-- https://tabler-icons.io/static/tabler-icons/icons-png/brand-headlessui.png -->
          <svg xmlns="http://www.w3.org/2000/svg" class="icon icon-tabler icon-tabler-brand-headlessui" width="24" height="24" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" fill="none" stroke-linecap="round" stroke-linejoin="round">
            <path stroke="none" d="M0 0h24v24H0z" fill="none"></path>
            <path d="M6.744 4.325l7.82 -1.267a4.456 4.456 0 0 1 5.111 3.686l1.267 7.82a4.456 4.456 0 0 1 -3.686 5.111l-7.82 1.267a4.456 4.456 0 0 1 -5.111 -3.686l-1.267 -7.82a4.456 4.456 0 0 1 3.686 -5.111z"></path>
            <path d="M7.252 7.704l7.897 -1.28a1 1 0 0 1 1.147 .828l.36 2.223l-9.562 3.51l-.67 -4.134a1 1 0 0 1 .828 -1.147z"></path>
          </svg>
        `,
      },
    ],
  },
  {
    name: "服务",
    page: "service",
    icon: html`
      <svg xmlns="http://www.w3.org/2000/svg" class="icon icon-tabler icon-tabler-layout-2" width="24" height="24" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" fill="none" stroke-linecap="round" stroke-linejoin="round"><path stroke="none" d="M0 0h24v24H0z" fill="none"></path><rect x="4" y="4" width="6" height="5" rx="2"></rect><rect x="4" y="13" width="6" height="7" rx="2"></rect><rect x="14" y="4" width="6" height="7" rx="2"></rect><rect x="14" y="15" width="6" height="5" rx="2"></rect></svg>
    `,
  },
  {
    name: "系统设置",
    also: "设置",
    list: [
      {
        name: "基础设置",
        page: "basic",
        icon: html`
          <svg xmlns="http://www.w3.org/2000/svg" class="icon icon-tabler icon-tabler-settings" width="24" height="24" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" fill="none" stroke-linecap="round" stroke-linejoin="round"><path stroke="none" d="M0 0h24v24H0z" fill="none"></path><path d="M10.325 4.317c.426 -1.756 2.924 -1.756 3.35 0a1.724 1.724 0 0 0 2.573 1.066c1.543 -.94 3.31 .826 2.37 2.37a1.724 1.724 0 0 0 1.065 2.572c1.756 .426 1.756 2.924 0 3.35a1.724 1.724 0 0 0 -1.066 2.573c.94 1.543 -.826 3.31 -2.37 2.37a1.724 1.724 0 0 0 -2.572 1.065c-.426 1.756 -2.924 1.756 -3.35 0a1.724 1.724 0 0 0 -2.573 -1.066c-1.543 .94 -3.31 -.826 -2.37 -2.37a1.724 1.724 0 0 0 -1.065 -2.572c-1.756 -.426 -1.756 -2.924 0 -3.35a1.724 1.724 0 0 0 1.066 -2.573c-.94 -1.543 .826 -3.31 2.37 -2.37c1 .608 2.296 .07 2.572 -1.065z"></path><circle cx="12" cy="12" r="3"></circle></svg>
        `,
      },
      {
        name: "用户管理",
        page: "users",
        icon: html`
          <!-- https://tabler-icons.io/static/tabler-icons/icons-png/users.png -->
          <svg xmlns="http://www.w3.org/2000/svg" class="icon icon-tabler icon-tabler-users" width="24" height="24" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" fill="none" stroke-linecap="round" stroke-linejoin="round">
            <path stroke="none" d="M0 0h24v24H0z" fill="none"></path>
            <path d="M9 7m-4 0a4 4 0 1 0 8 0a4 4 0 1 0 -8 0"></path>
            <path d="M3 21v-2a4 4 0 0 1 4 -4h4a4 4 0 0 1 4 4v2"></path>
            <path d="M16 3.13a4 4 0 0 1 0 7.75"></path>
            <path d="M21 21v-2a4 4 0 0 0 -3 -3.85"></path>
          </svg>
        `,
      },
      {
        name: "媒体库",
        page: "library",
        icon: html`
          <!-- https://tabler-icons.io/static/tabler-icons/icons-png/stereo-glasses.png -->
          <svg xmlns="http://www.w3.org/2000/svg" class="icon icon-tabler icon-tabler-stereo-glasses" width="24" height="24" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" fill="none" stroke-linecap="round" stroke-linejoin="round">
            <path stroke="none" d="M0 0h24v24H0z" fill="none"></path>
            <path d="M8 3h-2l-3 9"></path>
            <path d="M16 3h2l3 9"></path>
            <path d="M3 12v7a1 1 0 0 0 1 1h4.586a1 1 0 0 0 .707 -.293l2 -2a1 1 0 0 1 1.414 0l2 2a1 1 0 0 0 .707 .293h4.586a1 1 0 0 0 1 -1v-7h-18z"></path>
            <path d="M7 16h1"></path>
            <path d="M16 16h1"></path>
          </svg>
        `,
      },
      {
        name: "目录同步",
        page: "directorysync",
        icon: html`
          <!-- https://tabler-icons.io/static/tabler-icons/icons-png/refresh.png -->
          <svg xmlns="http://www.w3.org/2000/svg" class="icon icon-tabler icon-tabler-refresh" width="24" height="24" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" fill="none" stroke-linecap="round" stroke-linejoin="round">
            <path stroke="none" d="M0 0h24v24H0z" fill="none"></path>
            <path d="M20 11a8.1 8.1 0 0 0 -15.5 -2m-.5 -4v4h4"></path>
            <path d="M4 13a8.1 8.1 0 0 0 15.5 2m.5 4v-4h-4"></path>
          </svg>
        `,
      },
      {
        name: "消息通知",
        page: "notification",
        icon: html`
          <!-- https://tabler-icons.io/static/tabler-icons/icons-png/bell.png -->
          <svg xmlns="http://www.w3.org/2000/svg" class="icon icon-tabler icon-tabler-bell" width="24" height="24" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" fill="none" stroke-linecap="round" stroke-linejoin="round">
            <path stroke="none" d="M0 0h24v24H0z" fill="none"></path>
            <path d="M10 5a2 2 0 0 1 4 0a7 7 0 0 1 4 6v3a4 4 0 0 0 2 3h-16a4 4 0 0 0 2 -3v-3a7 7 0 0 1 4 -6"></path>
            <path d="M9 17v1a3 3 0 0 0 6 0v-1"></path>
          </svg>
        `,
      },
      {
        name: "过滤规则",
        page: "filterrule",
        icon: html`
          <!-- https://tabler-icons.io/static/tabler-icons/icons-png/filter.png -->
          <svg xmlns="http://www.w3.org/2000/svg" class="icon icon-tabler icon-tabler-filter" width="24" height="24" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" fill="none" stroke-linecap="round" stroke-linejoin="round">
            <path stroke="none" d="M0 0h24v24H0z" fill="none"></path>
            <path d="M5.5 5h13a1 1 0 0 1 .5 1.5l-5 5.5l0 7l-4 -3l0 -4l-5 -5.5a1 1 0 0 1 .5 -1.5"></path>
          </svg>
        `,
      },
      {
        name: "自定义识别词",
        page: "customwords",
        icon: html`
          <!-- https://tabler-icons.io/static/tabler-icons/icons-png/a-b.png -->
          <svg xmlns="http://www.w3.org/2000/svg" class="icon icon-tabler icon-tabler-a-b" width="24" height="24" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" fill="none" stroke-linecap="round" stroke-linejoin="round">
            <path stroke="none" d="M0 0h24v24H0z" fill="none"></path>
            <path d="M3 16v-5.5a2.5 2.5 0 0 1 5 0v5.5m0 -4h-5"></path>
            <path d="M12 6l0 12"></path>
            <path d="M16 16v-8h3a2 2 0 0 1 0 4h-3m3 0a2 2 0 0 1 0 4h-3"></path>
          </svg>
        `,
      },
      {
        name: "媒体服务器",
        page: "mediaserver",
        icon: html`
          <!-- https://tabler-icons.io/static/tabler-icons/icons-png/server-cog.png -->
          <svg xmlns="http://www.w3.org/2000/svg" class="icon icon-tabler icon-tabler-server-cog" width="24" height="24" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" fill="none" stroke-linecap="round" stroke-linejoin="round">
            <path stroke="none" d="M0 0h24v24H0z" fill="none"></path>
            <path d="M3 4m0 3a3 3 0 0 1 3 -3h12a3 3 0 0 1 3 3v2a3 3 0 0 1 -3 3h-12a3 3 0 0 1 -3 -3z"></path>
            <path d="M12 20h-6a3 3 0 0 1 -3 -3v-2a3 3 0 0 1 3 -3h10.5"></path>
            <path d="M18 18m-2 0a2 2 0 1 0 4 0a2 2 0 1 0 -4 0"></path>
            <path d="M18 14.5v1.5"></path>
            <path d="M18 20v1.5"></path>
            <path d="M21.032 16.25l-1.299 .75"></path>
            <path d="M16.27 19l-1.3 .75"></path>
            <path d="M14.97 16.25l1.3 .75"></path>
            <path d="M19.733 19l1.3 .75"></path>
            <path d="M7 8v.01"></path>
            <path d="M7 16v.01"></path>
          </svg>
        `,
      },
      {
        name: "字幕",
        page: "subtitle",
        icon: html`
          <!-- https://tabler-icons.io/static/tabler-icons/icons-png/badge-cc.png -->
          <svg xmlns="http://www.w3.org/2000/svg" class="icon icon-tabler icon-tabler-badge-cc" width="24" height="24" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" fill="none" stroke-linecap="round" stroke-linejoin="round">
            <path stroke="none" d="M0 0h24v24H0z" fill="none"></path>
            <path d="M3 5m0 2a2 2 0 0 1 2 -2h14a2 2 0 0 1 2 2v10a2 2 0 0 1 -2 2h-14a2 2 0 0 1 -2 -2z"></path>
            <path d="M10 10.5a1.5 1.5 0 0 0 -3 0v3a1.5 1.5 0 0 0 3 0"></path>
            <path d="M17 10.5a1.5 1.5 0 0 0 -3 0v3a1.5 1.5 0 0 0 3 0"></path>
          </svg>
        `,
      },
    ],
  },
];

export class LayoutNavbar extends CustomElement {
  static properties = {
    layout_gopage: { attribute: "layout-gopage" },
    layout_userpris: { attribute: "layout-userpris", type: Array },
    _active_name: { state: true}
  };

  constructor() {
    super();
    this.layout_gopage = "";
    this.layout_userpris = navbar_list.map((item) => (item.name));
    this._active_name = "";
    this.classList.add("navbar","navbar-vertical","navbar-expand-lg","lit-navbar-fixed","lit-navbar","lit-navbar-hide-scrollbar");
  }

  firstUpdated() {
    // 加载页面
    if (this.layout_gopage) {
      navmenu(this.layout_gopage);
    } else if (window.history.state?.page) {
      //console.log("刷新页面");
      window_history_refresh();
    } else {
      // 打开第一个页面
      for (const item of navbar_list) {
        if (item.name === this.layout_userpris[0]) {
          navmenu(item.page ?? item.list[0].page);
          break;
        }
      }
      // 默认展开探索
      setTimeout(() => { this.show_collapse("ranking") }, 200);
    }
    // 删除logo动画 加点延迟切换体验好
    setTimeout(() => {
      document.querySelector("#logo_animation").remove();
      this.removeAttribute("hidden");
      document.querySelector("#page_content").removeAttribute("hidden");
      document.querySelector("layout-searchbar").removeAttribute("hidden");
    }, 200);
  }

  update_active(page) {
    this._active_name = page ?? window.history.state?.page;
    this.show_collapse(this._active_name);
  }

  show_collapse(page) {
    for (const item of this.querySelectorAll("[id^='lit-navbar-collapse-']")) {
      for (const a of item.querySelectorAll("a")) {
        if (page === a.getAttribute("data-lit-page")) {
          item.classList.add("show");
          this.querySelectorAll(`button[data-bs-target='#${item.id}']`)[0].classList.remove("collapsed");
          return;
        }
      }
    }
  }

  render() {
    return html`
      <style>
        
        .navbar {
          min-height: 3rem !important;
        }
        
        .navbar .input-group-flat:focus-within {
          box-shadow: none;
        }
        
        .nav-search-bar {
          padding-top: calc(env(safe-area-inset-top) + var(--safe-area-inset-top)) !important;
          padding-left: env(safe-area-inset-left) !important;
        }
        
        .lit-navar-close {
            margin-top: calc(env(safe-area-inset-top) + var(--safe-area-inset-top)) !important;
        }

        .lit-navbar-fixed {
          position:fixed;
          top:0;
          left:0;
          z-index:1031
        }

        .lit-navbar-canvas {
          width:calc(var(--tblr-offcanvas-width) - 120px)!important;
        }

        .theme-light .lit-navbar-canvas {
          background-color: rgb(231, 235, 239);
        }

        .lit-navar-close {
          position:fixed;
          top:0;
          left:calc(var(--tblr-offcanvas-width) - 120px);
          z-index:var(--tblr-offcanvas-zindex);
          width: 80px;
        }

        .lit-navbar-hide-scrollbar {
          overflow-y: scroll!important;
          overscroll-behavior-y: contain!important;
          scrollbar-width: none!important;
          -ms-overflow-style: none!important;
        }

        .lit-navbar-hide-scrollbar::-webkit-scrollbar {
          display: none;
        }

        .lit-navbar-nav {
          max-height:none!important;
        }

        .theme-light .lit-navbar {
          background-color: rgb(231, 235, 239, 0.5);
        }

        /* 屏蔽lg以下顶栏 */
        @media (max-width: 992px) {
          .lit-navbar {
            max-height:0!important;
            min-height:0!important;
            padding:0!important;
            margin:0!important;
          }
        }

        .theme-dark .lit-navbar-accordion-button {

        }
        .theme-light .lit-navbar-accordion-button {

        }
        .lit-navbar-accordion-button::after {
          
        }

        .lit-navbar-accordion-item, .lit-navbar-accordion-item-active {
          border-radius:0.75rem;
        }

        .theme-dark .lit-navbar-accordion-item:hover {
          background-color: #2a3551ca!important;
        }
        .theme-light .lit-navbar-accordion-item:hover {
          background-color: #fcfafec5!important;
        }

        .theme-dark .lit-navbar-accordion-item-active {
          background-color: #414d6dca!important;
        }
        .theme-light .lit-navbar-accordion-item-active {
          background-color: rgba(123, 178, 233, 0.5)!important;
          color: #000!important;
        }

      </style>
      <div class="container-fluid">
        <div class="offcanvas offcanvas-start d-flex lit-navbar-canvas shadow" tabindex="-1" id="litLayoutNavbar">
          <div class="d-flex flex-row flex-grow-1 lit-navbar-hide-scrollbar">
            <div class="d-flex flex-column flex-grow-1">
              <h1 class="mt-3" style="text-align:center;">
                <img src="../static/img/logo-blue.png" alt="NAStool" style="height:3rem;width:auto;">
              </h1>
              <div class="accordion px-2 py-2 flex-grow-1">
                ${navbar_list.map((item, index) => ( html`
                  ${this.layout_userpris.includes(item.name)
                  ? html`
                    ${item.list?.length > 0
                    ? html`
                      <button class="accordion-button lit-navbar-accordion-button collapsed ps-2 pe-1 py-2" style="font-size:1.1rem;" data-bs-toggle="collapse" data-bs-target="#lit-navbar-collapse-${index}" aria-expanded="false">
                        ${item.also??item.name}
                      </button>
                      <div class="accordion-collapse collapse" id="lit-navbar-collapse-${index}">
                        ${item.list.map((drop) => (this._render_page_item(drop, true)))}
                      </div>`
                    : this._render_page_item(item, false)
                    } `
                  : nothing }
                `))}
              </div>
            </div>
          </div>
        </div>
      </div>
    `;
  }

  _render_page_item(item, child) {
    return html`
    <a class="nav-link lit-navbar-accordion-item${this._active_name === item.page ? "-active" : ""} my-1 p-2 ${child ? "ps-3" : "lit-navbar-accordion-button"}" 
      href="javascript:void(0)" data-bs-dismiss="offcanvas" aria-label="Close"
      style="${child ? "font-size:1rem" : "font-size:1.1rem;"}"
      data-lit-page=${item.page}
      @click=${ () => { navmenu(item.page) }}>
      <span class="nav-link-icon" ?hidden=${!child} style="color:var(--tblr-body-color);">
        ${item.icon ?? nothing}
      </span>
      <span class="nav-link-title">
        ${item.also ?? item.name}
      </span>
    </a>`    
  }

}


window.customElements.define("layout-navbar", LayoutNavbar);