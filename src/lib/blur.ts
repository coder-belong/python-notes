/**
 * 按 Esc 关弹窗、抽屉时调用：把焦点从打开它的按钮上拿掉。
 *
 * 用鼠标点按钮打开弹窗，焦点会留在这个按钮上；之后按 Esc 关掉弹窗，
 * 浏览器认为「刚才用的是键盘」，就会给这个按钮画一圈蓝色焦点框（:focus-visible），看着像 bug。
 */
export function blurActive(): void {
  const el = document.activeElement;
  if (el instanceof HTMLElement) el.blur();
}
