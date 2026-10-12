import java.io.File;
import java.util.Arrays;
import javax.tools.JavaCompiler;
import javax.tools.Diagnostic;
import javax.tools.DiagnosticCollector;
import javax.tools.JavaFileObject;
import javax.tools.StandardJavaFileManager;
import javax.tools.ToolProvider;
import com.sun.source.util.JavacTask;
public class ParseAndroidJava {
    public static void main(String[] args) throws Exception {
        JavaCompiler c = ToolProvider.getSystemJavaCompiler();
        DiagnosticCollector<JavaFileObject> diagnostics = new DiagnosticCollector<>();
        try(StandardJavaFileManager manager = c.getStandardFileManager(diagnostics, null, null)) {
            Iterable<? extends JavaFileObject> files=manager.getJavaFileObjectsFromFiles(Arrays.stream(args).map(File::new).toList());
            JavacTask task=(JavacTask)c.getTask(null,manager,diagnostics,Arrays.asList("-proc:none"),null,files);
            int parsed=0;
            for(var unit:task.parse()){ parsed++; System.out.println("PARSED "+unit.getSourceFile().getName()); }
            long errors=diagnostics.getDiagnostics().stream().filter(d->d.getKind()==Diagnostic.Kind.ERROR).count();
            for(var d:diagnostics.getDiagnostics()) System.err.println(d.getKind()+" "+d.getMessage(null));
            if(errors>0 || parsed!=args.length) System.exit(1);
        }
    }
}