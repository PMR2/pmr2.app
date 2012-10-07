Changelog
=========

0.6 - Released (2012-10-03)
---------------------------

Sixth major release of PMR2 Core, with major focus on user interfaces.

* Fork/Pull from other workspaces

  - This feature allows the forking/pulling of workspaces within PMR2,
    and pulling data from external repositories of the same type.

* Exposure wizard

  - This replaces the exposure builder/file type selection with a more
    streamlined interface.  This is constructed on top of the original
    framework.
  - Migration to updated exposure file types.  This indicates to users
    that the views specified have changed, and they are given a button
    to activate at their leisure to convert their file over to enable
    the usage of the new set of views defined for that file type.

* Exposure export/import, exposure rollover slight overhaul.

  - It is possible to export the exposure structure and import it into
    another workspace on the same or different PMR2 instance (provided
    that the same structure is supported).  This will lead into the
    wizard.
  - Exposure rollover will display the exposure structure using the
    wizard instead of recreating the entire structure right away.  This
    redirection allows better error handling.
  - Error handling leveraged includes the notification of renamed or
    missing files in the target commit for a given exposure, instead of
    returning a server error message.

* Curation moved to pmr2.annotation.curation

  - This library now provides better curation facilities, such as
    administration defined flags, with user-side selection widget to
    assign those defined values to a curation annotation on a file.

* Documentation generation is now tracked by an annotation.

* Default exposure file type is provided, as it is now very difficult
  for end users to assign views manually to an exposure file.

* Internal changes and other bug fixes.

  - All page layout/wrapper from the plone.z3cform classes have been
    removed as supporting this system has become quite a task when the
    adapter based layout is possible.  If the correct browser class for
    a view within PMR2 is correctly defined (which is by inheriting the
    browser classes within PMR2), the only changes required will be the
    removal of the wrappers and then update the zcml to point to the
    original unwrapped class.
  - The implementation for the vocabulary `pmr2.vocab.manifest` has
    been corrected once more to return the listing of files of the
    correct commit as specified by context (either through the object,
    form or request).  This is achieved by using this vocab in the
    conjunction with pmr2.app.workspace.schema.StorageFileChoice.

0.5.1 - Released (2012-06-28)
-----------------------------

* Bug-fix release.

  - The exposure file listings for the exposure documentation and the
    file builder form should return the correct list of files.

0.5 - Released (2012-02-13)
---------------------------

* Deprecation and form cleanups

  - Corrected the iro (interface resolution order) for the layer such
    that the authenticator is always rendered.
  - Removed pmr2.app.contents as that was deprecated and marked for
    removal.

* Annotator now adapts both context and request to be more compatible
  with typical usage.

0.4 - Released (2011-10-03)
---------------------------

* Major reorganization done to the code base.

  - The code is in the process of being split up and reorganized based
    on related features.  Most notable changes are the workspace and
    exposures being moved into its own module, with all supporting code
    elsewhere (such as subscribers and adapters) are moved into them.

* Introduction of customized renders of files directly from workspace

  - Workspace file views now supports the rendering of other file types,
    with the rendering controlled by the mimetype of the file.  Adapters
    can be registered to introduce customized renders for file types.
  - Exposures may be hooked into this method in the future, once an
    appropriate caching mechanism is put into place as the rendering of
    a custom type can trigger CPU intensive processes to construct the
    output that the client expects.
  - Default rendering of images and safe rendering of HTML are views
    that are now provided.

* Generalized workspace storage backend

  - While the plan for PMR2 was to allow multiple backends to be
    supported, it had strong ties to pmr2.mercurial.  This has been
    corrected as workspace now supports different backends.
  - Developers to create their own backends for the storage of data
    within PMR2, provided that the backend provides the output in the
    format PMR2 expects.  Also, even in the case of existing backends,
    a newer/better implementation can be more easily created to replace
    deprecated ones.

0.3.7 - Released (2011-07-13)
-----------------------------

* CSRF fix backported from development branch.

  - https://tracker.physiomeproject.org/show_bug.cgi?id=2976

0.3.6 - Released (2011-04-05)
-----------------------------

* Removed the ability to render arbitrary HTML for supported browsers 
  in the workspace viewer.

  - https://tracker.physiomeproject.org/show_bug.cgi?id=2878

0.3.5 - Released (2011-02-15)
-----------------------------

* Corrected dependency on deprecated packages.

  - https://tracker.physiomeproject.org/show_bug.cgi?id=2835

0.3.4 - Released (2011-01-18)
-----------------------------

* Backported changes made in master (trunk) that allow an exposure
  rollover to use a source exposure that does not reside in the default
  exposure container.

  - https://tracker.physiomeproject.org/show_bug.cgi?id=2806

* Reapplied some patches that were meant to be patched.

  - Exposure custom traversal should be fixed for good, this time.

0.3.3 - Released (2010-12-31)
-----------------------------

* Fresh installation now works as intended on standard configurations as
  the bugs that prevented this were fixed.

  - Settings now provides a method set up the objects and directories
    on disk.

    - https://tracker.physiomeproject.org/show_bug.cgi?id=2622

  - Default installation now correctly allow Mercurial clients to prompt
    users for authentication.

    - https://tracker.physiomeproject.org/show_bug.cgi?id=2625

  - PMR2 no longer prevents a default Plone site from rendering if it is
    present but not installed using the portal add-on installer tool.

    - https://tracker.physiomeproject.org/show_bug.cgi?id=2626

0.3.2 - Released (2010-07-01)
-----------------------------

* Updated documentation and classifiers.
* License has been amended to be what is intended (MPL/GPL/LGPL tri-
  license).

0.3.1 - Released (2010-06-22)
-----------------------------

* Fixed bugs that manifested in a virtual host environment.

  - exposure creation (both normal and rollover).
  - listing of exposures in the workspace pages.

* Removed placeholder subrepo list bullets.

0.3 - Released (2010-06-21)
---------------------------

Changes added in:

*0.3rc1*

* Streamlined exposure creation process.

  - Added a exposure file type definition object, which allows 
    repository managers to define a profile for different files, such
    that users can use it to generate consistent view listings with
    the correct tags (subject) attached to the file.
  - This also allows users to fill in all the data for all the views in
    a single form, rather than loading forms for every view they want to
    assign to the file if the file type is not defined for the file they
    want to create an exposure of.

* Added a global settings object, and added hooks to allow modules of
  PMR2 to have their own subforms.
* Added user workspaces - users can have their own folder to add
  their personal workspaces to.
* Added semi-edited note.  Enabled the use case where users can fill in
  fields and then generate output based on what was entered and content
  of the anchor file.
* Added partial exposure id resolution, where a partial id entered will
  resolve to its full id and redirect to the complete link.
* Added migration step, made available under under portal_setup.
* Pushes to workspace now updates the modified date, so RSS feeds based
  on updates to workspaces can be generated.
* Redone the exposure creation form as it was insecure against errors.
* Simplfied redirection from relative links to files in exposures to
  workspace and refactored how this was done.
* Fixed the 'Views available' link to show the default view rather than
  downloading the file.
* Refactored catalog/indexing code.
* Removed nearly all CellML specific features.
* Removed the ExposureFilePage type (deprecated in v0.2).
* Removed the stale portlets for the above type.
* Removed nearly all methods from content type objects, mostly have to
  do with the usage of the index/catalog adapters.

0.2.2 - Released (2010-02-02)
-----------------------------

* Finishing the document view generation step will no longer trigger a
  file download.
* Added in opencell:externalurl rewriting, much like PCEnv as the
  specification states that the URL for an external file is a literal,
  so it cannot take advantage of the xml:base attribute for the
  normalization of URL to kick in.

0.2.1 - Released (2010-01-12)
-----------------------------

* Added missing function in ExposureFolder, now it will not block
  redirection of files that are in the workspace, and can now have
  documentation generated for it
* Removed file existence check in Exposures, such that all URIs that
  do not exist in Plone are redirected to the source workspace
* For Exposures, @@viewgen is renamed to @@docviewgen for consistency.
* Expired state now is coloured red for all users

0.2 - Released (2009-12-21)
---------------------------

With the following changes:

*0.2rc1*

* Rewrote how Exposures are done.  The pages have been made deprecated
  and replaced with Exposure Files, which are wrappers around the files
  that can be referenced by the exposure.  The views are now annotations
  to those files.
* Buildout includes other view specific for CellML (i.e. code generation
  and MathML).
* Documentation can be generated.  Ones currently builtin to PMR2 
  include HTML and reStructuredText.  The buildout includes ones for
  CellML files.
* Support for Mercurial subrepo for embedding workspaces within another.
* Fixed pushing to workspaces that are marked private using PAS
  (Pluggable Authentication System).
* Various UI refinements.

*0.2rc2*

* Document view generation no longer generates empty title and 
  description if it's unknown.
* HTML document view now generates title from head/title.
* Files can also have a seprate source document like exposure root.
* Fixed authentication issue for Mercurial v0.9.5

*0.2rc3*

* Shows the review state of an exposure to normal users by color coding
  them in the workspace changelog listing, and in the exposure views.

*0.2rc4*

* The pmr2 review state is now correctly reindexes all subobject of an
  exposure when its state changes.
* Freshly created workspace will have its empty file list correctly
  rendered.

*0.2rc5*

* Allow the editing/rearrangement of views in ExposureFile
* Documentation pages within an exposure can now reference files in
  embedded workspaces.

0.1.2 - Released (2009-07-23)
-----------------------------

* Made empty workspace not result in an error page.

0.1.1 - Released (2009-07-16)
-----------------------------

* Session label should mention OpenCell to avoid confusion.
* Fixed a minor rendering issue with MathML on empty models.
* Fixed keyword string generation.
* Made citation author list sort case agnostic.

0.1 - Released (2009-06-22)
---------------------------

* Initial release of the Physiome Model Repository 2.  This provides
  integration with Mercurial using the API through a wrapper module.
* Workspaces are objects that wrap around a Mercurial repository.
* Exposures are folder objects that references a specific changeset of
  a specific workspace.
* Exposure pages are pages that represent some files, and are grouped
  together by metapages.
* For detailed changes from initial development to this release, please
  consult the logs in the version control system.
