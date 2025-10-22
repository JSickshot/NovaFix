import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from database import DB

tree_usr = None

def styled_entry(parent, width=20):
    return tk.Entry(parent, width=width, font=("Segoe UI", 11),
                    bg="#222222", fg="white", insertbackground="white", relief="flat")

def styled_label(parent, text):
    return tk.Label(parent, text=text, font=("Segoe UI", 11, "bold"),
                    bg="black", fg="#DAA621")

def cargar_tab_usuarios(frame):
    global tree_usr

    form=ttk.LabelFrame(frame,text="Alta Usuario",style="Custom.TLabelframe")
    form.pack(fill="x",padx=10,pady=10)

    e_user=styled_entry(form,20)
    e_pass=styled_entry(form,20)
    cb_rol=ttk.Combobox(form,values=["sistemas","tecnico","ventas"],state="readonly")
    cb_rol.current(0)

    styled_label(form,"Usuario:").grid(row=0,column=0,sticky="w");e_user.grid(row=0,column=1)
    styled_label(form,"Contraseña:").grid(row=1,column=0,sticky="w");e_pass.grid(row=1,column=1)
    styled_label(form,"Rol:").grid(row=2,column=0,sticky="w");cb_rol.grid(row=2,column=1)

    def guardar():
        conn=sqlite3.connect(DB);c=conn.cursor()
        try:
            c.execute("INSERT INTO usuarios (username,password,rol) VALUES (?,?,?)",(e_user.get(),e_pass.get(),cb_rol.get()))
            conn.commit();messagebox.showinfo("OK","Usuario creado");cargar_listado()
        except sqlite3.IntegrityError: messagebox.showerror("Error","Usuario ya existe")
        conn.close()

    ttk.Button(form,text="Guardar",style="Custom.TButton",command=guardar).grid(row=3,column=0,pady=6)

    tree_usr=ttk.Treeview(frame,columns=("id","username","rol"),show="headings")
    for c in ("id","username","rol"): tree_usr.heading(c,text=c.capitalize())
    tree_usr.pack(fill="both",expand=True,padx=10,pady=5)

    def cargar_listado():
        for r in tree_usr.get_children(): tree_usr.delete(r)
        conn=sqlite3.connect(DB);c=conn.cursor()
        c.execute("SELECT id,username,rol FROM usuarios ORDER BY username")
        for row in c.fetchall(): tree_usr.insert("",tk.END,values=row)
        conn.close()

    def editar_usr(_evt=None):
        sel=tree_usr.selection()
        if not sel:return
        vals=tree_usr.item(sel[0])["values"];uid=vals[0]
        win=tk.Toplevel(frame);win.title("Editar Usuario");win.configure(bg="black")

        styled_label(win,"Usuario").grid(row=0,column=0,sticky="w")
        e_user=styled_entry(win,20);e_user.insert(0,vals[1]);e_user.grid(row=0,column=1)

        styled_label(win,"Contraseña").grid(row=1,column=0,sticky="w")
        e_pass=styled_entry(win,20);e_pass.grid(row=1,column=1)

        styled_label(win,"Rol").grid(row=2,column=0,sticky="w")
        cb=tk.Combobox(win,values=["sistemas","tecnico","ventas"],state="readonly");cb.set(vals[2]);cb.grid(row=2,column=1)

        def guardar():
            conn=sqlite3.connect(DB);c=conn.cursor()
            if e_pass.get().strip():
                c.execute("UPDATE usuarios SET username=?,password=?,rol=? WHERE id=?",(e_user.get(),e_pass.get(),cb.get(),uid))
            else:
                c.execute("UPDATE usuarios SET username=?,rol=? WHERE id=?",(e_user.get(),cb.get(),uid))
            conn.commit();conn.close();cargar_listado();win.destroy()
        tk.Button(win,text="Guardar",bg="#BD181E",fg="white",activebackground="#DAA621",activeforeground="black",command=guardar).grid(row=3,column=0,columnspan=2,pady=10)

    tree_usr.bind("<Double-1>",editar_usr)
    cargar_listado()

def refrescar_usuarios():
    try:
        for r in tree_usr.get_children(): tree_usr.delete(r)
        conn=sqlite3.connect(DB);c=conn.cursor()
        c.execute("SELECT id,username,rol FROM usuarios ORDER BY username")
        for row in c.fetchall(): tree_usr.insert("",tk.END,values=row)
        conn.close()
    except Exception as e:
        print("Error refrescando usuarios:", e)
