<%*
// ---------- 1. 动态日期与时间变量 ----------
const now = moment();                          // 当前时间对象
const dateStr = now.format("YYYY-MM-DD");      // 日期, 如 2024-05-01
const timeStr = now.format("HH:mm");           // 时间, 如 14:30
const dateTimeStr = now.format("YYYY-MM-DD HH:mm"); // 完整日期时间

// ---------- 2. 用户输入提示 ----------
// 指标名称 (必填, 用于标题与文件名)
const indicatorName = await tp.system.prompt("请输入指标名称 :");

// 指标分类 (可选, 用于归类, 如 大势形 / 超买超卖型)
const category = await tp.system.prompt("请输入指标分类 :", "");

// 使用方式 (可选, 多行输入)
const usage = await tp.system.prompt("请输入使用方式 (可留空):", "");

// 注意事项条数 (数字, 默认 3)
const noteCountRaw = await tp.system.prompt("请输入注意事项条数 (默认 3):", "3");
const noteCount = parseInt(noteCountRaw) || 3;

// ---------- 3. 条件判断: 分类是否填写 ----------
// 若填写了分类, 生成分类标签行; 否则留空
const categoryLine = category && category.trim() !== ""
  ? `> 分类: ${category.trim()}\n`
  : "";

// ---------- 4. 循环: 逐条收集注意事项 ----------
let notesBlock = "";
for (let i = 1; i <= noteCount; i++) {
  const noteItem = await tp.system.prompt(`请输入第 ${i} 条注意事项 (可留空):`, "");
  // 条件判断: 仅当用户填写内容时才写入该条
  if (noteItem && noteItem.trim() !== "") {
    notesBlock += `${i}. ${noteItem.trim()}\n`;
  } else {
    notesBlock += `${i}. \n`; // 留空占位, 便于后续补充
  }
}

// ---------- 5. 组装最终内容 ----------
// 若指标名称为空, 使用占位符避免标题为空
const title = indicatorName && indicatorName.trim() !== ""
  ? indicatorName.trim()
  : "未命名指标";

// 使用方式: 有内容则填入, 否则留空占位
const usageLine = usage && usage.trim() !== ""
  ? usage.trim()
  : "";

// 输出模板正文 (保持与现有笔记一致的 Markdown 结构)
tR += `## ${title}
${categoryLine}- 名称
	- ${title}
- 使用方式
	- ${usageLine}
- 注意
${notesBlock}
<!-- 创建时间: ${dateTimeStr} | 日期: ${dateStr} | 时间: ${timeStr} -->
`;
_%>