"""Gemeinsame Hilfsfunktionen für Mkid – ohne externe Netzwerkanfragen."""
from pathlib import Path
import csv, math
import matplotlib.pyplot as plt

def start():
    print("✓ Forschungsheft bereit! Tipp: Shift + Enter führt die Zelle aus.")

def bruchbalken(zaehler, nenner):
    if not isinstance(zaehler, int) or not isinstance(nenner, int) or nenner <= 0 or zaehler < 0:
        print("Bitte ganze Zahlen mit Zähler >= 0 und Nenner > 0 eingeben."); return
    n=max(1, math.ceil(zaehler/nenner))
    fig, ax=plt.subplots(figsize=(7, .9*n+1.1))
    for i in range(n):
        for j in range(nenner):
            k=i*nenner+j
            ax.barh(n-i-1, 1, left=j, height=.72, color="#3478f6" if k<zaehler else "#ecf1f7",edgecolor="#1f2d3d")
    ax.set_xlim(0,nenner);ax.set_ylim(-.7,n-.3);ax.axis('off')
    ax.set_title(f"{zaehler}/{nenner} = {zaehler/nenner:g}",loc='left')
    plt.show()

def lade_gps():
    pfad=Path(__file__).resolve().parent.parent/'data'/'gps_messung.csv'
    with pfad.open(encoding='utf-8') as f:
        return [{k:(float(v) if k!='sender' else v) for k,v in row.items()} for row in csv.DictReader(f)]

def schaetze_position(daten=None):
    """Gittersuche mit gleichen Gewichten: Ort mit kleinster quadratischer Abweichung."""
    if daten is None: daten=lade_gps()
    bester_fehler=float('inf'); position=(None,None)
    for x in range(-35,36):
        for y in range(-35,36):
            fehler=sum((math.hypot(x-d['x_m'],y-d['y_m'])-d['gemessene_entfernung_m'])**2 for d in daten)
            if fehler<bester_fehler:
                bester_fehler=fehler;position=(x,y)
    return position

def zeichne_ortung(x,y,unsicherheit=20,daten=None):
    fig, ax=plt.subplots(figsize=(7,6))
    ax.scatter([x],[y],c='#3478f6',s=65,label='Geschätzter Ort',zorder=5)
    kreis=plt.Circle((x,y),unsicherheit,color='#3478f6',alpha=.14,lw=2)
    ax.add_patch(kreis)
    ax.add_patch(plt.Circle((x,y),unsicherheit,fill=False,color='#3478f6',lw=2,ls='--'))
    ax.plot(0,0,'k+',ms=12,mew=2,label='Referenzpunkt Physikbereich')
    ax.axhline(0,color='gray',lw=.5);ax.axvline(0,color='gray',lw=.5)
    ax.set_xlim(-35,40);ax.set_ylim(-35,40);ax.set_aspect('equal')
    ax.set_xlabel('Ost-West-Abstand x (m)');ax.set_ylabel('Nord-Süd-Abstand y (m)')
    ax.set_title('Modellierte Ortung: Bereich statt exakter Raum')
    ax.grid(alpha=.25);ax.legend(loc='upper right');plt.show()


def zeichne_schulkarte(x=None, y=None, unsicherheit=20, leere_karte=False):
    """Grobe Grundrissskizze in lokalen Metern, bewusst KEINE exakte Bauzeichnung.

    Schüler sehen keinen eingetragenen 'wahren' Roboterort.
    Fensterfront oben ca. 15 m, Gangbreite ca. 2 m.
    """
    from matplotlib.patches import Rectangle, Circle
    fig, ax = plt.subplots(figsize=(12, 9))
    fig.patch.set_facecolor('#f7f9fd')
    ax.set_facecolor('#f7f9fd')
    # Lokales schematisches Modell; orange Bezugspunkt (0, 0) in Sammlung.
    rooms = [
    ('Sammlung', -2, -2, 5, 5),
    ('224', 3, -2, 6, 5),
    ('Glasflur', 9, -2, 4, 5),
    ('222', -2, -9, 6, 5),
    ('221', 4, -9, 5, 5)
]
    for name,rx,ry,rw,rh in rooms:
        ax.add_patch(Rectangle((rx,ry),rw,rh,facecolor='#e8edf5',edgecolor='#2d3646',lw=2,zorder=1))
        ax.text(rx+rw/2,ry+rh/2,name,ha='center',va='center',fontsize=12,weight='bold',color='#2d3646')
    ax.text(3.9,3.15,'Fensterfront nach Süden (insgesamt ca. 15 m)',ha='center',fontsize=10)
    ax.text(3.2,-2.25,'Gang (ca. 2 m)',ha='center',fontsize=10)
    ax.plot(0,0,'o',color='#f39c12',markersize=9,zorder=6,label='Bezugspunkt')
    if not leere_karte and x is not None and y is not None:
        ax.add_patch(Circle((x,y),unsicherheit,facecolor='#60bafb',edgecolor='none',alpha=.16,zorder=3))
        ax.add_patch(Circle((x,y),unsicherheit,facecolor='none',edgecolor='#2785c4',ls='--',lw=2,zorder=4))
        ax.plot(x,y,'o',color='#2785c4',markersize=9,zorder=5,label='Berechneter Messpunkt')
    ax.set_xlim(-3, 14);ax.set_ylim(-10, 5)
    ax.set_aspect('equal');ax.grid(alpha=.15)
    ax.set_xlabel('x (m), schematisch');ax.set_ylabel('y (m), schematisch')
    ax.set_title('Physikbereich: grobe Raumskizze und Ortungsunsicherheit')
    ax.legend(loc='upper right')
    plt.show()
