import { html, nothing } from "../../utility/lit-core.min.js";
import { CustomElement } from "../../utility/utility.js";


export class LayoutSearchbar extends CustomElement {
  static properties = {
    layout_systemflag: { attribute: "layout-systemflag" },
    layout_username: { attribute: "layout-username" },
    layout_userpris: { attribute: "layout-userpris", type: Array },
  };

  constructor() {
    super();
    this.layout_systemflag = "Docker";
    this.layout_username = "admin";
    this.layout_userpris = ["系统设置"];
    this.classList.add("navbar", "fixed-top");
  }

  // 卸载事件
  disconnectedCallback() {
    super.disconnectedCallback();
  }


  render() {
    return html`
      <style>
      </style>
      <div class="container-fluid nav-search-bar">
        <div class="d-flex flex-row flex-grow-1 align-items-center py-1">
          <!-- 导航展开按钮 -->
          <layout-navbar-button></layout-navbar-button>
          <!-- 搜索栏 -->
          <div class="input-group input-group-flat mx-2">
            <h2 class="page-title">我的媒体库</h2>
          </div>
          <!-- 头像 -->
          <div class="nav-item dropdown me-2">
              <a href="#" class="nav-link d-flex lh-1 text-reset ms-1 p-0" data-bs-toggle="dropdown">
                <!-- http://tabler-icons.io/i/user -->
                <svg xmlns="http://www.w3.org/2000/svg" class="icon icon-tabler icon-tabler-user"
                    width="24" height="24" viewBox="0 0 24 24"
                    stroke-width="2" stroke="currentColor" fill="none" stroke-linecap="round" stroke-linejoin="round">
                  <path stroke="none" d="M0 0h24v24H0z" fill="none"></path>
                  <circle cx="12" cy="7" r="4"></circle>
                  <path d="M6 21v-2a4 4 0 0 1 4 -4h4a4 4 0 0 1 4 4v2"></path>
                </svg>
              </a>
              <div class="dropdown-menu dropdown-menu-end dropdown-menu-arrow">
                <a class="dropdown-item hide-theme-dark" href="?theme=dark" role="button">暗黑风格</a>
                <a class="dropdown-item hide-theme-light" href="?theme=light" role="button">明亮风格</a>
                <div class="dropdown-divider"></div>
                ${this.layout_userpris.includes("系统设置")
                ? html`
                    <a class="dropdown-item" data-bs-toggle="offcanvas" href="#offcanvasEnd" role="button"
                      aria-controls="offcanvasEnd">消息中心</a>
                    <a class="dropdown-item" href="javascript:show_logging_modal()" role="button">实时日志</a>
                    <div class="dropdown-divider"></div>
                    ${["Docker", "Synology"].includes(this.layout_systemflag)
                    ? html`
                      <a href="javascript:restart()" class="dropdown-item">重启</a>
                      <a href="javascript:update()" class="dropdown-item">更新</a>`
                    : nothing }
                  `
                : nothing }
                <a href="javascript:logout()" class="dropdown-item">
                  注销 <span class="text-muted mx-3">${this.layout_username}</span>
                </a>
              </div>
            </div>
          </div>
      </div>
    `;
  }

}


window.customElements.define("layout-searchbar", LayoutSearchbar);