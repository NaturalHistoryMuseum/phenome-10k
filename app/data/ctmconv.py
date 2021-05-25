import trimesh
from openctm import CTM, import_mesh, export_mesh

def ctmconv(source, dest):
	mesh = trimesh.load(source)
	ctm = CTM(mesh.vertices, mesh.faces, mesh.face_normals)
	export_mesh(ctm, dest)
