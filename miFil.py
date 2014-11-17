# coding=UTF-8
import sublime, sublime_plugin, os, re
import dircache

ID_VISTA = 0;
VISTA_LOAD_AQUI = None#con dobleclick abrirá el archivo en esta vista
OMITIR=[]#contiene los file_exclude_patterns del setting de ST2, para filtrar las carpetas
RUTAS=[]#cada item n del array es la ruta de la línea n mostrada
class unclickEnArchivo(sublime_plugin.TextCommand):
  def run_(self, args):
    #v = self.view
    #if v.id() == ID_VISTA: v.sel().clear()
    if 'command' in args:
      self.view.run_command(args['command'], args)
    else:
      self.view.run_command('drag_select', args)
class dblclickEnArchivoCommand(sublime_plugin.TextCommand):
  #si hacen doble click en un archivo del view con archivo .fil intentamos abrir el archivo clicado en el anterior view
  def run_(self, args):
    v = self.view
    ini = v.sel()[0].begin()
    print (v.sel())
    if v.id() == ID_VISTA: #sólo controlamos doble click en el view que tenga el .fil cargado
      global VISTA_LOAD_AQUI
      global RUTAS
      ruta = v.substr(v.line(ini)).strip().lstrip("/").strip()
      if ruta.startswith("colapsadas="):
        v.sel().clear()
        return
      fila = v.rowcol(ini)[0]
      if fila >= len(RUTAS): return
      ruta = RUTAS[fila] + ruta
      ruta = ruta.replace("\\","/")
      if os.path.isfile(ruta):
        if VISTA_LOAD_AQUI is None: VISTA_LOAD_AQUI=v
        ventana = VISTA_LOAD_AQUI.window()
        if ventana is None: ventana=v.window()
        ventana.focus_view(VISTA_LOAD_AQUI)
        ventana.open_file(ruta)
        VISTA_LOAD_AQUI=None
      else:#es carpeta
        #con doble click en carpeta la plegamos/deplegamos
        #esta llamada siguiente rellena las dos variables!!
        cerradas, regionColapsadas = obtenColapsadas(v)
        #buscamos el principio de línea tipo '   /' para buscar el siguiente con igual o menos espacios
        patron = v.substr(v.line(ini))#texto de linea actual antera
        patron = re.search(r"^\s+(?=/)",patron).group() #algo como '   '
        patron = r"\n\s{0," + str(len(patron)) + "}\S"#el regex: algo como \n\s{0,6}\S

        ini = v.text_point(fila+1, 0)
        fin = v.find(patron, ini)#buscamos desde char 0 de la linea actual + 1
        if fin is None:
          fin = v.size()
        else: 
          fin=fin.begin()
        v.sel().clear()
        ini -=1
        #descomentar para seleccionar la region en vez de plegarla
        #v.sel().add(sublime.Region(ini, fin))
        ruta = ruta.lower()
        plegada = v.fold(sublime.Region(ini, fin))
        if plegada:#true si NO estaba plegada
          cerradas.append(ruta)
        else:#YA estaba plegada
          v.unfold(sublime.Region(ini, fin))          
          if ruta in cerradas: cerradas.remove(ruta)
        v.set_read_only(False)
        edit = v.begin_edit("mifil")#guardamos línea 'colapsadas=rutas'        
        print "*".join(cerradas)
        #añadimos salto de línea al final porque si la líea es muy larga y hacen clic en la zona vacía de
        #debajo, se va el cursor al final del texto
        v.replace(edit, regionColapsadas, "colapsadas=" + ("*".join(cerradas).strip("\n")) + "\n")
        v.end_edit(edit)
        v.set_read_only(True)
        v.window().run_command("save")
    else:#doble click por defecto
      if 'command' in args:
        v.run_command(args['command'], args)
      else:
        v.run_command('drag_select', args)
    VISTA_LOAD_AQUI = None#limpiamos para no dejar la vista pillada aquí

class archivoFilCargado(sublime_plugin.EventListener):
  ultimo=0#incremento de los caracteres escritos
  cerradas = []#carpetas colapsadas
  def on_activated(self, view):
    if view is None or view.file_name() is None: return #evitamos que no sea una vista previa (preview)
    if view.file_name().endswith(".fil"):
      global ID_VISTA
      global RUTAS
      global OMITIR
      TABS = 0#tabulaciones
      #esto debería hacerse una vez al iniciar pero no me funcionaba bien. perdemos un poco de tiempo.
      OMITIR = view.settings().get("file_exclude_patterns")
      OMITIR = [x.replace('*', '') for x in OMITIR]
      ID_VISTA=view.id()
      self.cerradas, regionColapsadas, noestaba = obtenColapsadas(view)
      view.sel().clear()

      def bucledir(ad):
        #la madre del cordero. bucle que escribe cada línea si es distinta.
        #ad es un directorio (antiguamente 'a'rchivo'd'irectorio)
        #sólo se escribe una línea si cambia para evitar cambios en el scroll o los folds.
        #en un principio se borraba y reescribía todo el texto pero se perdía cada vez el scroll.
        archs=[]#archivos en este directorio
        self.TABS +=3
        for ad1 in dircache.listdir(ad):
          if os.path.isdir(ad + os.sep + ad1):
            RUTAS.append(ad + os.sep)
            txOld = view.substr(view.full_line(self.ultimo))
            txNew = (" " * self.TABS) + "/" + ad1 + "\n"
            if txOld != txNew:
              view.replace(edit, view.full_line(self.ultimo),txNew)
            self.ultimo +=len(txNew)
            inicioReg = self.ultimo -1
            bucledir(ad + os.sep + ad1)
            ruta = (ad + os.sep + ad1).lower().replace("\\","/")
            if ruta in self.cerradas:#si estaba colapsada la colapsamos
              view.fold(sublime.Region(inicioReg, self.ultimo - 1))
            if noestaba:#si estaba colapsada la colapsamos
              view.fold(sublime.Region(inicioReg, self.ultimo - 1))
              self.cerradas.append(ruta)
          else:#es un archivo, éstos los guardamos para escribirlos al final de la carpeta actual
            ext = os.path.splitext(ad1)[1]
            if not (ext in OMITIR or ad1 in OMITIR):#aquí ext va con punto (.php) pq también comparamos el archivo entero (.htaccess)
              ext = ext.lstrip(".")
              archs.append(type("", (), dict( arch= ad1, direc= ad + os.sep, ext= ext))())#objeto anónimo
        for arch in archs:
          indxIcon = self.ultimo + self.TABS - 2
          txOld = view.substr(view.full_line(self.ultimo))
          txNew = (" " * self.TABS) + arch.arch + "\n"
          if txOld != txNew:
            view.replace(edit, view.full_line(self.ultimo), txNew)
          self.ultimo +=len(txNew)
          #recuperamos el scope de lo que acabamos de escribir.
          #antiguamente recuperábamos las extensiones desde el archivo .tmLanguaje, pero era poco práctico.
          scop = view.scope_name(self.ultimo - 2).split(" ")
          ext = "otros"
          if "mifil" in scop: ext = scop[1]
          #esto dibuja el "icono"
          view.add_regions("reg" + str(indxIcon),[sublime.Region(indxIcon, indxIcon+1)], ext)
          RUTAS.append(arch.direc)
        self.TABS -=3

      view.set_read_only(False)
      view.set_scratch(True)#?¿?
      edit = view.begin_edit("mifil")
      self.TABS = 0
      RUTAS = []
      #view.erase(edit, sublime.Region(0, view.size()))
      #mejor usamos el parent dir del archivo .fil, no window.folders(),
      #así es más controlable, pues .window podría no tener carpetas.
      #aunque también podría tener más de una en la raíz. vaya.
      sdir = os.path.dirname(view.file_name())
      self.ultimo = 0
      txOld = view.substr(view.full_line(self.ultimo))
      txNew = (" " * self.TABS) + os.path.basename(sdir) + "\n"
      if txOld != txNew:
        view.replace(edit, view.full_line(self.ultimo), txNew)
      self.ultimo += len(txNew)
      RUTAS.append(os.path.dirname(sdir) + os.sep)
      TABS +=3
      #EMPIEZA EL BUCLE
      bucledir(sdir)
      #guardamos la línea con las carpetas colapsadas.
      #de paso borramos posible texto residual que haya quedado si por ejemplo han borrado un archivo.
      view.replace(edit, sublime.Region(self.ultimo, view.size()), "colapsadas=" + ("*".join(self.cerradas).strip("\n")) + "\n")

      try:
        view.end_edit(edit)
      finally:
        view.set_read_only(True)
        view.settings().set("color_scheme", sublime.packages_path()+"/miFil/miFil.tmTheme")
        view.window().run_command("save")

  def on_deactivated(self,view):
    if view.window() is None : return #si la han cerrado, por ejemplo
    global VISTA_LOAD_AQUI
    VISTA_LOAD_AQUI = view


def obtenColapsadas(v):
  #busca la línea que empieza por 'colapsadas=' que contiene las carpetas colapsadas la última vez que se grabó el archivo.
  #así no hay que colapsarlas a mano cada vez que se abre el .fil
  #devuelve el texto de la línea y la region.
  #obviamente la línea siempre estará al final del archivo. y tiene un scope con el color del fondo.
  regionColapsadas = v.find("(?<=\\n)colapsadas=.*", 0)
  noestaba = False
  if regionColapsadas == None:
    noestaba = True
    regionColapsadas = sublime.Region(v.size(), v.size())
  cerradas = v.substr(regionColapsadas).strip("\n")
  if cerradas.startswith("colapsadas="): cerradas = cerradas[len("colapsadas="):]
  cerradas = cerradas.strip().split("*")
  if "" in cerradas: cerradas.remove("")
  return cerradas, regionColapsadas, noestaba


# for x in xrange(1,5):#limpia la consola
#   print
# print "-------inicio miFil-----"








