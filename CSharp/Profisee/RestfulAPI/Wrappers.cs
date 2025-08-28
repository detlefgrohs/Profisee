using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Common {
    public  class Wrappers {
        static public void WrapWithTryCatch(string message, Action<LogLevel, string> LoggerAction, Action action) {
            try {
                action();
            } catch (Exception exception) {
                LoggerAction(LogLevel.Error, $@"{message}
Exception: {exception.Message}
{exception.StackTrace}
");
                //                logger.LogError($@"{message}
                //Exception: {exception.Message}
                //{exception.StackTrace}
                //");
            }
        }
        static public T WrapWithTryCatch<T>(string message, Action<LogLevel, string> LoggerAction, Func<T> func) {
            try {
                return func();
            } catch (Exception exception) {
                LoggerAction(LogLevel.Error, $@"{message}
Exception: {exception.Message}
{exception.StackTrace}
");
                //                logger.LogError($@"{message}
                //Exception: {exception.Message}
                //{exception.StackTrace}
                //");
            }
            return default(T);
        }
    }
}
