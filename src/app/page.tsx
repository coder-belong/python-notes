import NotesApp from "@/components/NotesApp";
import { loadNotes } from "@/lib/notes";

// 构建时读 content/notes.md、转成 HTML；页面里的交互（目录、计时、勾选）在 NotesApp 里
export default function Page() {
  const notes = loadNotes();
  return <NotesApp notes={notes} />;
}
