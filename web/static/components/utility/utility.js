import { LitElement } from "./lit-core.min.js";

export class CustomElement extends LitElement {

  // 兼容前进后退时重载
  connectedCallback() {
    super.connectedCallback();
    this.innerHTML = "";
  }

  // 过滤空字符
  attributeChangedCallback(name, oldValue, newValue) {
    super.attributeChangedCallback(name, oldValue, Golbal.repNull(newValue));
  }

  // 不使用影子dom
  createRenderRoot() {
    return this;
  }

}

export class Golbal {

  // 没有图片时
  static noImage = "../static/img/no-image.png";
  static noImage_person = "../static/img/person.png";

  // 转换传值的空字符情况
  static repNull(value) {
    if (!value || value == "None" || value == "null" || value == "undefined") {
      return "";
    } else {
      return value;
    }
  }

  // 是否触摸屏设备
  static is_touch_device() {
    return "ontouchstart" in window;
  }

  static convert_mediaid(tmdbid) {
    if (typeof(tmdbid) === "number") {
      tmdbid = tmdbid + "";
    }
    return tmdbid
  }

  // 保存额外的页面数据
  static save_page_data(name, value) {
    const extra = window.history.state?.extra ?? {};
    extra[name] = value;
    window_history(false, extra);
  }

  // 获取额外的页面数据
  static get_page_data(name) {
    return window.history.state?.extra ? window.history.state.extra[name] : undefined;
  }
  
  // 判断直接获取缓存或ajax_post
  static get_cache_or_ajax(api, name, data, func) {
    const ret = Golbal.get_page_data(api + name);
    //console.log("读取:", api + name, ret);
    if (ret) {
      func(ret);
    } else {
      const page = window.history.state?.page;
      ajax_post(api, data, (ret) => {
        // 页面已经变化, 丢弃该请求
        if (page !== window.history.state?.page) {
          //console.log("丢弃:", api + name, ret);
          return
        }
        Golbal.save_page_data(api + name, ret);
        //console.log("缓存:", api + name, ret);
        func(ret)
      });
    }
  }

  // 共用的fav数据更改时刷新缓存
  static update_fav_data(api, name, func=undefined) {
    const key = api + name;
    let extra = Golbal.get_page_data(key);
    if (extra && func) {
      extra = func(extra);
      Golbal.save_page_data(key, extra);
      //console.log("更新fav", extra);
    }
  }

}