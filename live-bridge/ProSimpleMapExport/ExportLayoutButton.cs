using System;
using System.Linq;
using ArcGIS.Desktop.Core;
using ArcGIS.Desktop.Framework.Contracts;
using ArcGIS.Desktop.Framework.Dialogs;
using ArcGIS.Desktop.Framework.Threading.Tasks;
using ArcGIS.Desktop.Layouts;
using ArcGIS.Desktop.Mapping;

namespace ProSimpleMapExport
{
    /// <summary>
    /// Ribbon button: export the active layout (or the project's first layout) to a 300dpi PDF.
    ///
    /// This runs IN-PROCESS inside ArcGIS Pro, so it operates on the live, open project —
    /// exactly the "watch it happen in the app" experience an external ArcPy process cannot give.
    /// All ArcGIS objects must be touched on the MCT (main CIM thread) via QueuedTask.Run.
    /// </summary>
    internal class ExportLayoutButton : Button
    {
        protected override async void OnClick()
        {
            // 1) Pick an output path on the UI thread (SaveFileDialog is a WPF/UI-thread API).
            var dlg = new Microsoft.Win32.SaveFileDialog
            {
                Title = "导出布局为 PDF",
                Filter = "PDF 文件 (*.pdf)|*.pdf",
                FileName = "layout_export.pdf",
                OverwritePrompt = true
            };
            if (dlg.ShowDialog() != true)
                return; // user cancelled

            string outPath = dlg.FileName;

            try
            {
                // 2) Do all ArcGIS work on the MCT.
                string message = await QueuedTask.Run(() =>
                {
                    // Prefer the layout the user is currently looking at...
                    Layout layout = LayoutView.Active?.Layout;

                    // ...otherwise fall back to the first layout in the project.
                    if (layout == null)
                    {
                        LayoutProjectItem item =
                            Project.Current.GetItems<LayoutProjectItem>().FirstOrDefault();
                        layout = item?.GetLayout();
                    }

                    if (layout == null)
                        return "当前工程没有任何布局可以导出。";

                    var pdf = new PDFFormat
                    {
                        OutputFileName = outPath,
                        Resolution = 300,
                        DoCompressVectorGraphics = true,
                        ImageCompression = ImageCompression.Adaptive
                    };

                    if (!pdf.ValidateOutputFilePath())
                        return $"输出路径无效或被占用：{outPath}";

                    layout.Export(pdf);
                    return $"已导出布局「{layout.Name}」→\n{outPath}";
                });

                MessageBox.Show(message, "出图");
            }
            catch (Exception ex)
            {
                MessageBox.Show($"导出失败：{ex.Message}", "出图");
            }
        }
    }
}
