function (doc) {
  let list_tags = Object.keys(doc)
  delete list_tags[0];//deleting extra tags _id, _rev
  delete list_tags[1];
  let filtered = list_tags.filter(function (el) {
    return el != null;
  });
  emit(doc._id, filtered);
}