using ArcGIS.Desktop.Framework;
using ArcGIS.Desktop.Framework.Contracts;

namespace ProSimpleMapExport
{
    /// <summary>
    /// The add-in module. ArcGIS Pro instantiates exactly one of these and keeps it
    /// alive for the session. Buttons/tools belong to this module (see Config.daml).
    /// </summary>
    internal class Module1 : Module
    {
        private static Module1 _this = null;

        /// <summary>Singleton accessor (id must match insertModule id in Config.daml).</summary>
        public static Module1 Current =>
            _this ??= (Module1)FrameworkApplication.FindModule("ProSimpleMapExport_Module");

        /// <summary>Called when the module loads (autoLoad=true → at Pro startup). Start the bridge.</summary>
        protected override bool Initialize()
        {
            BridgeServer.Log("Module1.Initialize() called");
            try { BridgeServer.Start(); }
            catch (System.Exception ex) { BridgeServer.Log("Module1: Start threw: " + ex.Message); }
            return base.Initialize();
        }

        /// <summary>Called when Pro unloads the module. Stop the bridge.</summary>
        protected override void Uninitialize()
        {
            try { BridgeServer.Stop(); } catch { }
            base.Uninitialize();
        }

        /// <summary>Return true so Pro can unload the add-in cleanly.</summary>
        protected override bool CanUnload() => true;
    }
}
